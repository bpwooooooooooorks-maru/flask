from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import yt_dlp
import os
import requests

app = Flask(__name__)

# ダウンロードしたファイルを保存するディレクトリ
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_video(url):
    ydl_opts = {
        'format': 'bv+ba/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),  # 保存先を指定
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.route('/', methods=['GET', 'POST'])
def index():
    download_url = None

    # アクセス時にdownloadsフォルダ内のファイルを削除
    if os.path.exists(DOWNLOAD_FOLDER):
        for filename in os.listdir(DOWNLOAD_FOLDER):
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            try:
                os.remove(file_path)  # ファイルを削除
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

    if request.method == 'POST':
        url = request.form['url']
        r = requests.get(url)
        url = r.url
        download_video(url)

        # 最新のダウンロードされたファイルを取得
        files = os.listdir(DOWNLOAD_FOLDER)
        if files:
            download_url = files[-1]  # 最後にダウンロードしたファイル

        return render_template('index.html', download_url=download_url)

    return render_template('index.html')

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename,as_attachment=True, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(debug=True)
