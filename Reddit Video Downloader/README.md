# Reddit Video Downloader

A Python script which can be used to download Reddit Videos with a shareable link. This script solves the problem of Reddit not supporting direct links to Reddit hosted videos. Reddit sends streams of the video and the audio seperately. This script downloads it, MUXs it and outputs it to `output.mp4` file.

# Dependancies

- [ffmpeg](https://www.ffmpeg.org/) which is a software suite needed to MUX the audio and video received from Reddit. Download [this zip file](https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20191101-53c21c2-win64-static.zip) and extract the file called **ffmpeg.exe** to the same folder where **reddit-downloader.py** resides.

# How to run it

Download the three files namely `reddit-downloader.py`, `res.json`, and `ffmpeg` and copy them to the same folder. It's necessary to put them in the same folder.

Open `res.json` folder and edit it in the editor of your choice. If you haven't don't have a Reddit Account, create it. Enter your username and the password in the `USERNAME` and `PASSWORD` keys of the json file.

If you haven't created a Reddit App then create one. This is necessary to access the Reddit API without which Reddit will block you for sending too many requests with this script. Create a [Reddit App here](https://www.reddit.com/prefs/apps/) (You can set the redirect URL to http://localhost:8080/). For more details on how to create a Reddit App, refer [here](https://alpscode.com/blog/how-to-use-reddit-api/).

After creating the App, note down the `APP-ID` and the `APP-SECRET` and add it to the `res.json` file.

That's it! Just run **reddit-downloader.py** and enter the URL of the video you want to download.
