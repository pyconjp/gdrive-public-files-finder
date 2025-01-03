# gdrive-public-files-finder

Googleドライブ内のPyCon JPの共有ドライブにある公開されているファイルを探すスクリプト。
意図しない、公開されたままのファイルが存在すると危険なため、プログラムでファイルを探して非公開にする。

## 環境構築

```bash
% python3.12 -m venv env
% . env/bin/activate
(env) % pip install -r requirements.txt
```

## Google Cloudアプリの作成

* Google Cloudでアプリを作成
  * Google Drive APIとGoogle Sheets APIを有効化
* APIとサービス > OAuth同意画面でOAuthを設定
  * 公開ステータス: テスト中
  * テストユーザー: 自分のGoogleアカウント
  * （PyCon JPの共有ドライブにアクセス可能なGoogleアカウント）
* APIとサービス > 認証情報
  * OAuthクライアントIDを「デスクトップアプリ」で作成
  * JSONファイルをダウンロードして`credentials.json`として保存
  
## tokenの作成

`quickstart.py`を実行して、Webブラウザで自分のGoogleアカウントでGoogleドライブ、Googleスプレッドシートへのアクセスを許可する

```bash
(env) % python quickstart.py
```

## 参考

* Google Drive API
  * [Python quickstart  |  Google Drive  |  Google for Developers](https://developers.google.com/drive/api/quickstart/python)
  * [Method: files.list  |  Google Drive  |  Google for Developers](https://developers.google.com/drive/api/reference/rest/v3/files/list)
  * [Method: permissions.list  |  Google Drive  |  Google for Developers](https://developers.google.com/drive/api/reference/rest/v3/permissions/list)
  * [Method: permissions.delete  |  Google Drive  |  Google for Developers](https://developers.google.com/drive/api/reference/rest/v3/permissions/delete)
  * [REST Resource: files  |  Google Drive  |  Google for Developers](https://developers.google.com/drive/api/reference/rest/v3/files#File)
  * [REST Resource: permissions  |  Google Drive  |  Google for Developers](https://developers.google.com/drive/api/reference/rest/v3/permissions#Permission)
* Google Sheets API
  * [Python quickstart  |  Google Sheets  |  Google for Developers](https://developers.google.com/sheets/api/quickstart/python)
* [gspread — gspread 6.1.2 documentation](https://docs.gspread.org/en/latest/)
