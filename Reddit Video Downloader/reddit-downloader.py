# Reddit Video Downloader is a python script which uses reddit api and ffmpeg to download the video and audio streams from Reddit URLs and the MUX it into a single output file called "output.mp4"

import requests
import json
import os
import sys

# Opens res.json file and reads USERNAME, PASSWORD, Reddit APP-ID, Reddit APP-SECRET

with open("res.json", "r") as json_data:
    data = json.loads(json_data.read())

USERNAME = data["USERNAME"]
PASSWORD = data["PASSWORD"]
APP_ID = data["APP-ID"]
APP_SECRET = data["APP-SECRET"]
BOT_NAME = ""

#############################   DOWNLOADING AND GENERATING VIDEO    #############################


#########   PARSING URL   ######### 

# This takes the URL and checks if it is a valid "reddit" URL. If not, return -1.
# Then it removes everything after "?utm_source" and returns only the URL appended with ".json"
# Example - It takes a normal shareable link like - https://www.reddit.com/r/PewdiepieSubmissions/comments/dqj8vj/jesus_christ_is_that_pewdiepie/?utm_source=share&utm_medium=web2x
# and returns https://oauth.reddit.com/r/PewdiepieSubmissions/comments/dqj8vj/jesus_christ_is_that_pewdiepie.json
# oauth is used because the access token is only received from https://oauth.reddit.com
# This URL is returned. ".json" is appended because we will only be using the json object from the request to this URL.

def url_parser(url):
    
    if not("https://www.reddit.com/r/" in url):
        return -1
    index = url.find("?utm_source")
    mes = url
    if(index >= 0):
        mes = url[:index]
    if(mes[-1] == "/"):
        mes = mes[:len(mes)-1]
    mes = mes.replace("www.reddit.com", "oauth.reddit.com")
    mes += ".json"
    return mes

#########   GETTING ACCESS TOKEN FROM REDDIT   #########

# This function gets the access token from reddit for the app we created. This access token is needed to receive data without getting blocked by reddit for repeated requests. It tries to get the access token 3 times and then returns -1 if it fails.

def get_access_token(count=0):
    print("Getting Access Token")
    base_url = 'https://www.reddit.com/'
    data = {'grant_type': 'password', 'username': USERNAME, 'password': PASSWORD}
    auth = requests.auth.HTTPBasicAuth(APP_ID, APP_SECRET)
    user_agent = BOT_NAME + " by " + USERNAME
    r = requests.post(base_url + 'api/v1/access_token', data=data, headers={'user-agent': user_agent}, auth=auth)
    if(r.status_code == 200):
        d = r.json()
        print(d)
        return d
    else:
        print("Error getting access token")
        if(count >= 3):
            print("Trying again : {}".format(count+1))
            return get_access_token(count+1)
        else:
            return -1 

#########   GETTING DATA FROM GIVEN URL   #########

# This uses the token from the get_access_token() method and uses it to get the json object of the reddit page. It'll try it three times, then returns -1 if it fails.

def get_data(d, url, count):
    print("Getting data - attempt " + str(count+1))
    if(count <=3):
        token = 'bearer ' + d['access_token']
        headers = {'Authorization': token, 'User-Agent': 'DownloadBot by sachihiroastra'}
        print("Getting response")
        response = requests.get(url, headers=headers)
    else:
        print("Error getting data. Returning")
        return -1
    print("Got Response")
    dat = response.json()
    if response.status_code == 200:
        return download_data(dat)
    else:
        print("Failed. Trying again")
        d = get_access_token()
        count += 1
        get_data(d, url, count)


#########   DOWNLOADING AUDIO/VIDEO AND MUXING IT   #########

# This does the actual work. This extracts the fallback_url from the reddit link and then uses it to download the video. A traditional fallback url looks like this - https://v.redd.it/453sfaasfas/DASH_XXX?source=fallback This is then outputted to test.mp4
# Everything starting from the DASH_XXX is removed and replaced with "audio" to get the audio stream of the video. This is then outputted to test.mp3
# Then the command line tool - ffmpeg is used to MUX these two streams together and output it to output.mp4. It also deletes test.mp4 and test.mp3 automatically.

def download_data(dat):
    print("Downloading data")
    mes = dat[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]
    ind = mes.find("DASH")
    mes2 = mes[0:ind]
    mes2 += "audio"
    
    try:
        with requests.get(mes, stream=True) as rv:
            rv.raise_for_status()
            total_size = int(rv.headers.get('content-length', 0))
            print("Got Response for video. Size = {}".format(total_size))
            if(rv.status_code == 200):
                print("Downloading Video")
                with open("test.mp4", "wb") as f:
                    x = 0
                    for chunk in rv.iter_content(1024):
                        if chunk:
                            x += len(chunk)
                            line = "\rWritten " + str(x) + " out of " + str(total_size)
                            sys.stdout.write(line)
                            sys.stdout.flush()
                            f.write(chunk)
            else:
                print("Error Downloading video. Returning")
                return -1
    except requests.exceptions.HTTPError:
        return -1
    print()
    try:
        with requests.get(mes2, stream=True) as rv:
            rv.raise_for_status()
            total_size = int(rv.headers.get('content-length', 0))
            print("Got Response for audio. Size = {}".format(total_size))
            print("Got response for audio")
            if(rv.status_code == 200):
                print("Downloading audio")
                with open("test.mp3", "wb") as f:
                    x = 0
                    for chunk in rv.iter_content(1024):
                        if chunk:
                            x += len(chunk)
                            line = "\rWritten " + str(x) + " out of " + str(total_size)
                            sys.stdout.write(line)
                            sys.stdout.flush()
                            f.write(chunk)   
    except requests.exceptions.HTTPError:
        pass
    print()

    if(os.path.exists("output.mp4")):
            os.remove("output.mp4")

    if(os.path.exists("test.mp3")):
        print("MUXing video and audio")
        os.system("ffmpeg -i test.mp4 -i test.mp3 -c:v copy -c:a aac -strict experimental output.mp4")

    else:
        os.rename("test.mp4", "output.mp4")

    if(os.path.exists("test.mp4")):
        print("Deleting video file")
        os.remove("test.mp4")
    if(os.path.exists("test.mp3")):
        print("Deleting audio file")
        os.remove("test.mp3")

    return 1


def main():
    url = input("Enter URl")    
    url = url_parser(url)

    if(url == -1):
        print("Failed parsing")
        return
    
    d = get_access_token()
    if(d==-1):
        print("Failed getting access token")
        return

    x = get_data(d, url, 0)

    if(x == -1):
        print("Failed getting data")
        return
    
    print("Done")
    

if __name__ == "__main__":
    main()
