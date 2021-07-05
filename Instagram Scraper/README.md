## Disclaimer - This script if used with profiles with large number of posts can cause Instagram to block your account. Use a throwaway account if required

# Instagram Scraper

<p align="center">
<a href="https://www.python.org/"><img alt="Python Version"src = "https://img.shields.io/pypi/pyversions/ansicolortags.svg" ></a> <a href = "https://www.linux.org/">
<img alt="PowerShell Gallery" src="https://img.shields.io/powershellgallery/p/Az?color=blue&logo=linux&logoColor=white"> </a>
</p>

A python script which when given a username downloads all posts (images and videos) from instagram. Even private profiles are scraped provided user follows them.

## How to use
Download the file `insta-scraper.py` place it in desired directory. Open the file and replace `USERNAME` and `PASSWORD` with your username and password. This is required for scraping private profiles. Also replace `SCRAPE_USERNAME` with the username to be scraped

Run the script and voila! Your job is done.

### Usage 
```
python insta-scraper.py
```

__Note:__ Profiles with large number of posts can take a long while and might not work owing to the fact that Instagram might rate limit the requests.
