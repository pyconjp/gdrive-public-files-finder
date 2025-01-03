import os
from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import gspread

# サービスアカウントの認証情報
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]

# Google Driveのファイルから取得する情報
# https://developers.google.com/drive/api/reference/rest/v3/files
FILE_FIELDS = {
    "id": "ID",
    "name": "名前",
    "webViewLink": "URL",
    "mimeType": "種類",
    "modifiedTime": "最終更新",
}

# MIMEタイプと日本語名の対応表
# https://developers.google.com/drive/api/guides/mime-types?hl=ja
MIME_TYPES = {
    "application/vnd.google-apps.document": "Googleドキュメント",
    "application/vnd.google-apps.drive-sdk": "サードパーティのショートカット",
    "application/vnd.google-apps.drawing": "Google図形描画",
    "application/vnd.google-apps.file": "Googleドライブファイル",
    "application/vnd.google-apps.folder": "Googleドライブフォルダ",
    "application/vnd.google-apps.form": "Googleフォーム",
    "application/vnd.google-apps.fusiontable": "Google Fusion Tables",
    "application/vnd.google-apps.jam": "Google Jamboard",
    "application/vnd.google-apps.mail-layout": "メールのレイアウト",
    "application/vnd.google-apps.map": "Googleマイマップ",
    "application/vnd.google-apps.photo": "Googleフォト",
    "application/vnd.google-apps.presentation": "Googleスライド",
    "application/vnd.google-apps.script": "Google Apps Script",
    "application/vnd.google-apps.shortcut": "ショートカット",
    "application/vnd.google-apps.site": "Googleサイト",
    "application/vnd.google-apps.spreadsheet": "Googleスプレッドシート",
}

# 検索対象の共有フォルダのIDと、結果を保存するスプレッドシートのID
SHARED_FOLDERS = {
    # "PyCon JP": "0AB4V-gRXzKWgUk9PVA",
    "Python Boot Camp": (
        "0AHeZnmob9mlbUk9PVA", "1Jhv8DSZ1K2oUOP-2u7NoK5xEv6P6GW79PUrMtDrk9C0",
    ),
    # "PyCon JP Association": "0AKLhHa9lUV2NUk9PVA",
}


def is_public(service, file_id: str) -> bool:
    """
    ファイルが公開されているかpermissionを調べて返す
    """
    result = False

    # 任意のファイルの権限を取得する
    # https://developers.google.com/drive/api/reference/rest/v3/permissions/list
    data = service.permissions().list(
        fileId=file_id, supportsAllDrives=True).execute()

    # 権限の中に「anyone」が存在しら公開されている
    # https://developers.google.com/drive/api/reference/rest/v3/permissions
    permissions = data.get("permissions", [])
    for permission in permissions:
        if permission["type"] == 'anyone':
            result = True

    return result


def search_public_files(service, shared_folder_id: str) -> list:
    """共有フォルダ内の公開ファイルを検索する"""
    # https://developers.google.com/drive/api/guides/search-files

    results = []

    # ファイルから取得するフィールド情報をFILE_FIELDSから作成する
    # https://developers.google.com/drive/api/reference/rest/v3/files
    file_fields = ", ".join(FILE_FIELDS)
    fields = f"nextPageToken, files({file_fields})"

    while True:
        page_token = None

        # ファイルの一覧を取得する
        # 共有フォルダの場合はdriveID〜supportsAllDrivesの引数が必要（らしい）
        # https://developers.google.com/drive/api/reference/rest/v3/files/list
        files = service.files().list(
            driveId=shared_folder_id,
            corpora="drive",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            fields=fields,
            pageToken=page_token,
            pageSize=50,
        ).execute()
        items = files.get("files", [])

        if not items:
            break

        # itemの中に誰でも閲覧できるファイルがないか調べる
        for item in items:
            if is_public(service, item["id"]):
                # breakpoint()
                results.append(item)

        # 次のページを読み込み
        break
        page_token = files.get("nextPageToken")
        if page_token is None:
            break

    return results


def write_public_files_to_sheet(sheet, files: list):
    """公開されているファイルの一覧をスプレッドシートに書き込む"""
    worksheet = sheet.worksheet("共有ファイル一覧")
    # ヘッダー行を追加
    worksheet.append_row(list(FILE_FIELDS.values()))
    for file_ in files:
        # 値のリストを作成
        row = []
        for key in FILE_FIELDS:
            value = file_[key]
            if key == "mimeType":
                value = MIME_TYPES.get(value, value)
            elif key == "modifiedTime":
                value = f"{value[:10]} {value[11:19]}"
            row.append(value)
        worksheet.append_row(row, value_input_option="USER_ENTERED")


def main():
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    service = build("drive", "v3", credentials=creds)

    for name, (shared_folder_id, sheets_id) in SHARED_FOLDERS.items():
        print(f"{name}フォルダを調査")
        # 公開されているファイルの一覧を取得する
        public_files = search_public_files(service, shared_folder_id)
        print(f"{len(public_files)}の公開ファイルが見つかりました")

        # 結果をスプレッドシートに書き込む
        print("シートに書き込む")
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(sheets_id)
        write_public_files_to_sheet(sheet, public_files)


if __name__ == "__main__":
    main()
