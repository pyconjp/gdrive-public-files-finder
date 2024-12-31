import os

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# サービスアカウントの認証情報
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']  # 読み取り専用権限

# 検索対象の共有フォルダID
SHARED_FOLDER_IDS = [
    # "0AB4V-gRXzKWgUk9PVA",  # PyCon JP
    "0AHeZnmob9mlbUk9PVA",  # Python Boot Camp
    # "0AKLhHa9lUV2NUk9PVA",  # PyCon JP Association
]


def is_public(service, item):
    result = False

    data = service.permissions().list(
        fileId=item["id"], supportsAllDrives=True).execute()

    permissions = data.get("permissions", [])
    for permission in permissions:
        if permission["type"] == 'anyone':
            print(item["id"], item["name"])
            print(permission)
            result = True

    return result


def search_public_files(service, shared_folder_id):
    """共有フォルダ内の公開ファイルを検索する"""
    # https://developers.google.com/drive/api/guides/search-files

    results = []
    # query = "createdTime > '2017-06-01T12:00:00'"
    # query = ""

    while True:
        page_token = None

        files = service.files().list(
            corpora="drive",
            driveId=shared_folder_id,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            fields="nextPageToken, files(id, name, webViewLink)",
            pageToken=page_token,
            pageSize=1000,
        ).execute()
        items = files.get("files", [])

        if not items:
            break

        # itemの中に誰でも閲覧できるファイルがないか調べる
        for item in items:
            if is_public(service, item):
                results.append(item)

        page_token = files.get("nextPageToken")
        if page_token is None:
            break

    return results


def main():
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    service = build("drive", "v3", credentials=creds)

    for folder_id in SHARED_FOLDER_IDS:
        public_files = search_public_files(service, folder_id)

        if public_files:
            print("公開されているファイル:")
            for file in public_files:
                print(f"- {file['name']}: {file['webViewLink']}")
        else:
            print("公開されているファイルはありません。")



if __name__ == "__main__":
    main()
