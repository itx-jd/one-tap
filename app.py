from flask import Flask, jsonify
import yt_dlp
import requests
from bs4 import BeautifulSoup
import json
import re

app = Flask(__name__)

# Common utility functions

def clean_str(s):
    return json.loads('{"text": "' + s + '"}')['text']

# Facebook functions

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

def fetch_facebook_video_info(url):
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

        title = get_title(response.text)
        thumbnail_value = fetch_thumbnail(url)
        video_url = get_hd_link(response.text)
        video_url = video_url+ '&dl=1'

        return {'success': True,'title': title,'thumbnail': thumbnail_value,'video_url': video_url, }

    except requests.exceptions.RequestException as e:
        msg = {'success': False, 'message': str(e)}

# End of Facebook functions

# YouTube functions

def get_video_info(url):
    ydl_opts = {
        'format': 'best',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)

            title = info_dict.get('title')
            thumbnail_value = info_dict.get('thumbnail')
            video_url = info_dict.get('url')
           
            return {'success': True,'title': title,'thumbnail': thumbnail_value,'video_url': video_url, }

        except yt_dlp.utils.DownloadError as e:
            return {'success': False, 'error_message': str(e)}

# End of YouTube functions

# Flask routes

# Flask routes

@app.route('/<path:video_url>', methods=['GET'])
def get_video_info_endpoint(video_url):
    
    if video_url.lower() == 'favicon.ico':
        # Handle favicon.ico request (return an empty response or your favicon)
        return ''

    if video_url.startswith('videos/'):
        return jsonify({'success': False, 'error_message': 'Invalid video URL'})

    if 'facebook.com' in video_url or 'fb.watch' in video_url:
        result = fetch_facebook_video_info(video_url)
    else:
        result = get_video_info(video_url)

    response_data = {
            'success': True,
            'title': result['title'],
            'thumbnail': result['thumbnail'],
            'video_url': result['video_url']
        }

    return jsonify(response_data)

# Run the Flask app

if __name__ == '__main__':
    app.run(debug=True)
