import re
import requests
import os
import shutil
from datetime import datetime

# define constants
USERNAME = 'YOUR_USERNAME'
PASSWORD = 'YOUR_PASSWORD'
SCRAPE_USERNAME = 'USERNAME_TO_BE_SCRAPED'

base_url = "https://www.instagram.com"
link = 'https://www.instagram.com/accounts/login/'
login_url = 'https://www.instagram.com/accounts/login/ajax/'
scrape_url = 'https://www.instagram.com/graphql/query/?query_id=17888483320059182'
userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
time = int(datetime.now().timestamp())

""" 
function that returns the csrf token from instagram
@param session user session object
@returns csrf token
"""
def get_csrf_token(session):

    print("getting csrf token")

    session.headers = {"user-agent": userAgent}
    session.headers.update({"Referer": link})
    res = session.get(link)
    csrf = re.findall(r"csrf_token\":\"(.*?)\"", res.text)[0]
    print(f"received csrf token : {csrf}")
    return csrf


""" 
function that logins to instagram using the generated csrf token 
@param session user session object
@param csrf csrf token
"""
def login_to_instagram(session, csrf):

    print("logging in")

    payload = {
        'username': USERNAME,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{PASSWORD}',
        'queryParams': {},
        'optIntoOneTap': 'false'
    }
    res = session.post(login_url, data=payload, headers={
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://www.instagram.com/accounts/login/",
        "x-csrftoken": csrf
    })

    print("received login response : ")
    print(res.json())

    # confirm logged in
    response_json = res.json()
    if(response_json["authenticated"] != True):
        print("login failed")
        exit(1)

    print("login successful!")


""" 
function that gets the user of the profile to be scraped
this is used in graphql queries
@param session user session object
@param csrf csrf token
@returns userid of user to be scraped
"""
def get_userid(session, csrf):

    print("getting userid of user to be scraped")

    url = f'{base_url}/{SCRAPE_USERNAME}/?__a=1'

    res = session.get(url, headers={
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://www.instagram.com/accounts/login/",
        "x-csrftoken": csrf
    })

    response_json = res.json()
    userid = response_json["graphql"]["user"]["id"]

    print(f"got user id : {userid}") 

    return userid


""" 
function that gets media shortcodes of all posts
@param session user session object
@param csrf csrf token
@param userid userid of the profile to be scraped
@returns array of media shortcodes
"""
def get_media_shortcodes(session, csrf, userid):
    print("fetching all media links")
    url = f'{scrape_url}&id={userid}&first=20'

    res = session.get(url, headers={
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://www.instagram.com/accounts/login/",
        "x-csrftoken": csrf
    })
    response_json = res.json()

    media_shortcodes = []
    post_timestamps = []

    count = 1

    while(True):
        print(f"Processing page {count}")
        for edges in response_json["data"]["user"]["edge_owner_to_timeline_media"]["edges"]:
            print(f"received shortcode : {edges['node']['shortcode']}")
            media_shortcodes.append(edges["node"]["shortcode"])
            post_timestamps.append(edges["node"]["taken_at_timestamp"])

        end_cursor = response_json["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]

        if len(end_cursor) == 0:
            break

        print(f"received end cursor : {end_cursor}")

        nexturl = f'{url}&after={end_cursor}'

        res = session.get(nexturl, headers={
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": csrf
        })
        response_json = res.json()

        count += 1

    print(media_shortcodes)
    return media_shortcodes, post_timestamps


""" 
function that gets downloadable media links from media shortcodes 
@param session user session object
@param csrf csrf token
@param media_shortcodes array of media shortcodes
@returns array of media links
"""
def get_media_links(session, csrf, media_shortcodes, post_timestamps):
    count = 1
    index = 0
    media_links = []
    media_timestamps = []
    for shortcode in media_shortcodes:
        url = f"https://www.instagram.com/p/{shortcode}/?__a=1"
        res = session.get(url, headers={
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": csrf
        })

        response_json = res.json()
        media_json = response_json["graphql"]["shortcode_media"]
        
        # if a post has multiple media as carousal
        if "edge_sidecar_to_children" in media_json:
            offset = 0
            for edge in media_json["edge_sidecar_to_children"]["edges"]:
                count += 1
                # check if media is video or image
                if("video_url" in edge['node']):
                    print(f"found link {count} : {edge['node']['video_url']}")
                    media_links.append(f"1{edge['node']['video_url']}")
                    media_timestamps.append(post_timestamps[index]+offset)
                else: 
                    print(f"found link {count} : {edge['node']['display_url']}")
                    media_links.append(edge['node']['display_url'])
                    media_timestamps.append(post_timestamps[index]+offset)
                offset += 1
                    
        else:
            count += 1
            if("video_url" in media_json):
                    print(f"found link {count} : {media_json['video_url']}")
                    media_links.append(f"1{media_json['video_url']}")
                    media_timestamps.append(post_timestamps[index])
            else:
                print(f"found link {count} : {media_json['display_url']}")
                media_links.append(media_json['display_url'])
                media_timestamps.append(post_timestamps[index])
        
        index += 1

    print(f"final count : {len(media_links)}")
    return media_links, media_timestamps

""" 
function that downloads media and writes to file
also creates folder 
@param session user session object
@param csrf csrf token
@param media_links array of media_links
"""
def download_media(session, csrf, media_links, media_timestamps):
    count = 1

    # deleting directory if exists
    current_directory = os.path.abspath(os.getcwd())
    dir = f'{current_directory}/{SCRAPE_USERNAME}'
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

    for link in media_links:
        extension = "jpg"
        # check if link is video
        if(link[0] == '1'):
            link = link[1:]
            extension = "mp4"

        print(f"writing media {count} : {link}")

        # stream data for performance reasons
        with session.get(link, headers={
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": csrf
        }, stream=True) as r:

            r.raise_for_status()
            with open(f"{dir}/{count}.{extension}", 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        os.utime(f'{dir}/{count}.{extension}', (media_timestamps[count-1], media_timestamps[count-1]))
        
        count += 1

def main(): 
    # start a user session
    session = requests.Session()

    # get csrf token
    csrf = get_csrf_token(session=session)

    # login
    login_to_instagram(session=session, csrf=csrf)

    # get user id of user to be scraped
    userid = get_userid(session=session, csrf=csrf)

    # get all media shortcodes
    media_shortcodes, post_timestamps = get_media_shortcodes(session=session, csrf=csrf, userid=userid)
    
    # get all media links from shortcodes
    media_links, media_timestamps = get_media_links(session=session, csrf=csrf, media_shortcodes=media_shortcodes, post_timestamps=post_timestamps)

    # download media
    download_media(session=session, csrf=csrf, media_links=media_links, media_timestamps=media_timestamps)

    print("successfully scraped!")

if __name__ == '__main__':
    main()
