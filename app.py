from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os
import re
import requests

app = Flask(__name__)

# ダウンロードしたファイルを保存するディレクトリ
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_video(url, userid):
    ydl_opts = {
        'format': 'bv+ba/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{userid}_%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.route('/', methods=['GET', 'POST'])
def index():
    download_urls = []
    downloaded_filenames = set()  # 保存したファイル名を追跡するセット

    # アクセス時にdownloadsフォルダ内のファイルを削除
    if os.path.exists(DOWNLOAD_FOLDER):
        for filename in os.listdir(DOWNLOAD_FOLDER):
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

    if request.method == 'POST':
        urls = request.form.getlist('url')
        for url in urls:
            try:
                r = requests.get(url)
                final_url = r.url
                match = re.search(r'@([^/]+)', final_url)
                if match:
                    userid = match.group(1)
                else:
                    userid = 'unknown'  # useridが見つからなかった場合のデフォルト値

                # URLが新しい場合のみダウンロード
                # ユーザーIDと動画IDを元に一意なファイル名を生成
                file_name_template = f'{userid}_%(id)s.mp4'

                # ダウンロードする前にファイル名をチェック
                with yt_dlp.YoutubeDL({'outtmpl': os.path.join(DOWNLOAD_FOLDER, file_name_template)}) as ydl:
                    info_dict = ydl.extract_info(url, download=False)
                    file_name = ydl.prepare_filename(info_dict)

                if file_name not in downloaded_filenames:
                    download_video(final_url, userid)

                    # ダウンロードしたファイル名を追加
                    download_urls.append(os.path.basename(file_name))
                    downloaded_filenames.add(file_name)  # 実際のファイル名を追跡
            except Exception as e:
                print(f"Error downloading {url}: {e}")

        return render_template('index.html', download_urls=download_urls)

    return render_template('index.html')

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(debug=True)
