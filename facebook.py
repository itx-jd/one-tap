import requests
from bs4 import BeautifulSoup
import json
import re

def clean_str(s):
    return json.loads('{"text": "' + s + '"}')['text']

def get_hd_link(content):
    regex_rate_limit = r'browser_native_hd_url":"([^"]+)"'
    match = re.search(regex_rate_limit, content)
    return clean_str(match.group(1)) if match else None

def get_title(content):
    title = None
    match = re.search(r'<title>(.*?)<\/title>', content)
    if match:
        title = match.group(1)
    else:
        match = re.search(r'title id="pageTitle">(.+?)<\/title>', content)
        if match:
            title = match.group(1)
    return clean_str(title) if title else None

def fetch_thumbnail(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        key_value_pairs = {}

        for tag in soup.find_all('meta'):
            if tag.get('property') == 'og:image' and tag.get('content'):
                thumbnail_url = tag['content']
                return thumbnail_url

    return json.dumps({'error': 'Failed to retrieve thumbnail'})

def fetch_video_info(url):
    headers = {
        'sec-fetch-user': '?1',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-site': 'none',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'cache-control': 'max-age=0',
        'authority': 'www.facebook.com',
        'upgrade-insecure-requests': '1',
        'accept-language': 'en-GB,en;q=0.9,tr-TR;q=0.8,tr;q=0.7,en-US;q=0.6',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()

        msg = {'success': True}
        msg['title'] = get_title(response.text)
        msg['thumbnail'] = fetch_thumbnail(url)

        hd_link = get_hd_link(response.text)

        if hd_link:
            msg['video_url'] = hd_link + '&dl=1'
        else:
            msg['video_url'] = None

    except requests.exceptions.RequestException as e:
        msg = {'success': False, 'message': str(e)}

    return json.dumps(msg)

def facebook_extractor(url):
    return fetch_video_info(url)

# Example usage for fetching video information
video_info_result = facebook_extractor("https://www.facebook.com/reel/1108744950305974")
print(video_info_result)
