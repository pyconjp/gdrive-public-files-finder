"""公開ファイルから公開の権限を削除する"""

import gspread
from googleapiclient.discovery import build

from find_public_files import get_credentials, SHARED_FOLDERS


def remove_permission_by_id(service, file_id: str, permission_id: str):
    """指定されたpermissionをファイルから削除する"""
    # https://developers.google.com/drive/api/reference/rest/v3/permissions/delete
    results = service.permissions().delete(
        fileId=file_id,
        permissionId=permission_id,
        supportsAllDrives=True,
    ).execute()
    return results


def remove_public_permission(sheet, service):
    """スプレッドシートの内容を読み込み、ファイルを非公開にする"""
    worksheet = sheet.worksheet("公開ファイル一覧")
    for row in worksheet.get_all_records():
        # 公開列に文字列が入っているファイルは対象外
        if row["公開"]:
            continue

        # permissionsを取得
        # https://developers.google.com/drive/api/reference/rest/v3/permissions/list
        results = service.permissions().list(
            fileId=row["ID"],
            supportsAllDrives=True,
        ).execute()

        for permission in results["permissions"]:
            # 公開パーミッションを削除する
            if permission["type"] == "anyone":
                remove_permission_by_id(service, row["ID"], permission["id"])
        print(f'{row["名前"]}を非公開にしました')


def main():
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    for name, (_, sheets_id) in SHARED_FOLDERS.items():
        print(f"\n{name}フォルダのファイルを処理")

        # スプレッドシートから情報を読み込む
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(sheets_id)
        remove_public_permission(sheet, service)


if __name__ == "__main__":
    main()
