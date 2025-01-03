import os
import time
from datetime import datetime
from random import random

import gspread
from gspread.exceptions import APIError
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# サービスアカウントの認証情報
SCOPES = [
    "https://www.googleapis.com/auth/drive",
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
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "MS Word",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "MS PowerPoint",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "MS Excel",
    "application/vnd.ms-excel": "MS Excel",
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "application/pdf": "PDF",
}

# 検索対象の共有フォルダのIDと、結果を保存するスプレッドシートのID
SHARED_FOLDERS = {
    "Python Boot Camp": (
        "0AHeZnmob9mlbUk9PVA",
        "1Jhv8DSZ1K2oUOP-2u7NoK5xEv6P6GW79PUrMtDrk9C0",
    ),
    "PyCon JP Association": (
        "0AKLhHa9lUV2NUk9PVA",
        "1i4Tx83Bx5l16o_1jMWDxZCoIu_7p-ATzB5VAN-ZCCm8",
    ),
    "PyCon JP": ("0AB4V-gRXzKWgUk9PVA", "1Rpc6rJY5DI1-oRiMz5vYMEUrDMXCa1CRGyAMwxcdYl0"),
}


def get_credentials():
    """クレデンシャルを返す"""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def search_public_files(service, shared_folder_id: str) -> list:
    """共有フォルダ内の公開ファイルを検索する"""
    # https://developers.google.com/drive/api/guides/search-files

    results = []
    page_token = None

    # ファイルから取得するフィールド情報をFILE_FIELDSから作成する
    # https://developers.google.com/drive/api/reference/rest/v3/files
    file_fields = ", ".join(FILE_FIELDS)
    fields = f"nextPageToken, files({file_fields})"

    # 公開ファイルのみを示す検索条件
    # https://developers.google.com/drive/api/guides/ref-search-terms
    query = "visibility = 'anyoneCanFind' or visibility = 'anyoneWithLink'"

    while True:
        # ファイルの一覧を取得する
        # 共有フォルダの場合はdriveID〜supportsAllDrivesの引数が必要（らしい）
        # https://developers.google.com/drive/api/reference/rest/v3/files/list
        files = (
            service.files()
            .list(
                q=query,
                driveId=shared_folder_id,
                corpora="drive",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                fields=fields,
                pageToken=page_token,
                pageSize=1000,
            )
            .execute()
        )
        items = files.get("files", [])

        if not items:
            break

        results.extend(items)

        # 次のページを読み込み
        page_token = files.get("nextPageToken")
        if page_token is None:
            break

    return results


def retry_append_row(worksheet, row: list[str], max_retries=5, initial_delay=5):
    """リクエストに失敗したときにリトライする"""
    for attempt in range(max_retries):
        try:
            worksheet.append_row(row, value_input_option="USER_ENTERED")
            return
        except APIError as e:
            # レート制限
            if e.code == 429:
                delay = initial_delay * (2**attempt) + random()
                print(f"リクエストが失敗（code: {e.code}）")
                print(
                    f"{delay:.2f}秒後にリトライ(試行回数: {attempt + 1}/{max_retries})"
                )
                time.sleep(delay)
            else:
                raise  # レート制限以外のエラーはそのまま例外を上げる
    raise Exception(f"リクエストが最大試行回数({max_retries})を超えました。")


def write_public_files_to_sheet(sheet, files: list):
    """公開されているファイルの一覧をスプレッドシートに書き込む"""
    worksheet = sheet.worksheet("公開ファイル一覧")
    # データを削除
    worksheet.clear()
    # ヘッダー行を追加
    headers = list(FILE_FIELDS.values())
    headers.append(f"更新日時: {datetime.now()}")
    worksheet.append_row(headers)

    rows = []
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

        rows.append(row)

    # 公開されている全ファイルの情報をまとめて追加
    worksheet.append_rows(rows, value_input_option="USER_ENTERED")


def main():
    creds = get_credentials()
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
