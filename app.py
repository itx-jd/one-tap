from flask import Flask, jsonify
import yt_dlp

app = Flask(__name__)

def get_video_info(url):
    ydl_opts = {
        'format': 'best',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)

            url_value = info_dict.get('url')
            title_value = info_dict.get('title')
            thumbnail_value = info_dict.get('thumbnail')
            
        except yt_dlp.utils.DownloadError as e:
            return str(e), None, None  # Handle invalid URLs gracefully

    return url_value, thumbnail_value, title_value

@app.route('/<path:video_url>', methods=['GET'])
def get_video_info_endpoint(video_url):
    if video_url.lower() == 'favicon.ico':
        # Handle favicon.ico request (return an empty response or your favicon)
        return ''

    if video_url.startswith('videos/'):
        return jsonify({'error': 'Invalid video URL'})

    url_value, thumbnail_url, video_title = get_video_info(video_url)

    if url_value is None:
        return jsonify({'error': 'Invalid video URL'})

    response_data = {
        'video_link': url_value,
        'thumbnail_url': thumbnail_url,
        'video_title': video_title
    }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
