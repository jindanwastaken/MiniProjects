import re
import requests
import os
import shutil
from datetime import datetime
import logging

logging.basicConfig(filename='insta-downloader.log', level=logging.DEBUG)

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

TOTAL_POST_COUNT = 0

""" 
function that returns the csrf token from instagram
@param session user session object
@returns csrf token
"""
def get_csrf_token(session):

    logging.info("inside csrf function")
    print("getting csrf token")

    try:
        session.headers = {"user-agent": userAgent}
        session.headers.update({"Referer": link})
        res = session.get(link)
        logging.info("csrf request made")
        logging.info(res.text)
        csrf = re.findall(r"csrf_token\":\"(.*?)\"", res.text)[0]
        print(f"received csrf token : {csrf}")
        logging.info(f"received csrf token : {csrf}")
        return csrf

    except Exception as e:
        print("error occurred")
        logging.error("error while getting csrf token")
        logging.error(e)
        exit(1)


""" 
function that logins to instagram using the generated csrf token 
@param session user session object
@param csrf csrf token
"""
def login_to_instagram(session, csrf):

    logging.info("inside login to instagram function")
    print("logging in")

    try:
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
        logging.info(res.json())
        print("received login response : ")
        print(res.json())

        # confirm logged in
        response_json = res.json()
        if(response_json["authenticated"] != True):
            print("login failed")
            logging.error("login failed")
            exit(1)

    except Exception as e:
        print("error while logging in")
        logging.error("error while logging in")
        logging.error(e)
        exit(1)

    logging.info("login success")
    print("login successful!")


""" 
function that gets the user of the profile to be scraped
this is used in graphql queries
@param session user session object
@param csrf csrf token
@returns userid of user to be scraped
"""
def get_userid(session, csrf):

    logging.info("inside get_userid function")
    print("getting userid of user to be scraped")

    try:
        url = f'{base_url}/{SCRAPE_USERNAME}/?__a=1'

        res = session.get(url, headers={
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": csrf
        })

        logging.info(res.json())

        response_json = res.json()
        userid = response_json["graphql"]["user"]["id"]

        logging.info(f"user id : {userid}")
        print(f"got user id : {userid}") 
    
    except Exception as e:
        print("error occurred while fetching userid")
        logging.error("error occurred while fetching userid")
        logging.error(e)
        exit(1)

    return userid


""" 
function that gets media shortcodes of all posts
@param session user session object
@param csrf csrf token
@param userid userid of the profile to be scraped
@returns array of media shortcodes
"""
def get_media_shortcodes(session, csrf, userid):

    global TOTAL_POST_COUNT
    
    logging.info("inside get media shortcodes function")

    print("fetching all media links")
    try:
        url = f'{scrape_url}&id={userid}&first=20'

        res = session.get(url, headers={
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": csrf
        })
        response_json = res.json()
        logging.info(response_json)

        media_shortcodes = []
        post_timestamps = []

        count = 1

        while(True):
            print(f"Processing page {count}")
            logging.info(f"Processing page {count}")
            for edges in response_json["data"]["user"]["edge_owner_to_timeline_media"]["edges"]:
                print(f"received shortcode : {edges['node']['shortcode']}")
                logging.info(f"received shortcode : {edges['node']['shortcode']}, timestamp : {edges['node']['taken_at_timestamp']}")
                media_shortcodes.append(edges["node"]["shortcode"])
                post_timestamps.append(edges["node"]["taken_at_timestamp"])
                count += 1

            end_cursor = response_json["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]

            if len(end_cursor) == 0:
                break

            print(f"received end cursor : {end_cursor}")
            logging.info(f"received end cursor : {end_cursor}")

            nexturl = f'{url}&after={end_cursor}'

            res = session.get(nexturl, headers={
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
                "referer": "https://www.instagram.com/accounts/login/",
                "x-csrftoken": csrf
            })
            response_json = res.json()
            logging.info(response_json)

        TOTAL_POST_COUNT = count

    except Exception as e:
        print("error while making request for media short codes")
        logging.error("error while making request for media short codes")
        logging.error(e)
        exit(1)

    print(media_shortcodes)
    logging.info(media_shortcodes)
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

    global TOTAL_POST_COUNT

    logging.info("inside get media links function")
    print("fetching media links")

    for shortcode in media_shortcodes:
        try:
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
                        print(f"found link {count} / {TOTAL_POST_COUNT} : {edge['node']['video_url']}")
                        media_links.append(f"1{edge['node']['video_url']}")
                        media_timestamps.append(post_timestamps[index]+offset)
                    else: 
                        print(f"found link {count} / {TOTAL_POST_COUNT} : {edge['node']['display_url']}")
                        media_links.append(edge['node']['display_url'])
                        media_timestamps.append(post_timestamps[index]+offset)
                    offset += 1
                        
            else:
                count += 1
                if("video_url" in media_json):
                        print(f"found link {count} / {TOTAL_POST_COUNT} : {media_json['video_url']}")
                        media_links.append(f"1{media_json['video_url']}")
                        media_timestamps.append(post_timestamps[index])
                else:
                    print(f"found link {count} / {TOTAL_POST_COUNT} : {media_json['display_url']}")
                    media_links.append(media_json['display_url'])
                    media_timestamps.append(post_timestamps[index])
            
            index += 1
        except Exception as e:
            print(f"error occurred while converting {shortcode} to media link")
            logging.error(f"error occurred while converting {shortcode} to media link")
            logging.error(e)

    TOTAL_POST_COUNT = count
    print(f"final count : {count}")
    logging.info(f"final count : {count}")
    logging.info(media_links)
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

    global TOTAL_POST_COUNT
    logging.info("inside download media function")
    print("downloading media")

    # deleting directory if exists
    current_directory = os.path.abspath(os.getcwd())
    dir = f'{current_directory}/{SCRAPE_USERNAME}'
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

    for link in media_links:
        try:
            extension = "jpg"
            # check if link is video
            if(link[0] == '1'):
                link = link[1:]
                extension = "mp4"

            print(f"writing media {count} / {TOTAL_POST_COUNT} : {link}")

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

        except Exception as e:
            print(f"error occurred when downloading from {link}")
            logging.error(f"error occurred when downloading from {link}")
            logging.error(e)
    
    print(f"total {count} / {TOTAL_POST_COUNT} downloaded")
    logging.info(f"total {count} / {TOTAL_POST_COUNT} downloaded")

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
