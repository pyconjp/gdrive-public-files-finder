# gdrive-public-files-finder

Googleドライブ内のPyCon JPの共有ドライブにある公開されているファイルを探すスクリプト。
意図しない、公開されたままのファイルが存在すると危険なため、プログラムでファイルを探して非公開にする。

## 環境構築

```bash
% python3.12 -m venv env
% . env/bin/activate
(env) % pip install -r requirements.txt
```

## アプリの作成

* Google Cloudでアプリを作成
  * Google Drive APIを有効化
* APIs & Services > OAuth consent screenでOAuthを設定
* API & Services > Credentials

## 参考

* [Python quickstart  |  Google Drive  |  Google for Developers](https://developers.google.com/drive/api/quickstart/python)
  * [Python のクイックスタート  |  Google Drive  |  Google for Developers](https://developers.google.com/drive/api/quickstart/python?hl=ja)
