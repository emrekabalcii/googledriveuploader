from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import argparse

def authenticate_google_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("token.saved")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("token.saved")
    drive = GoogleDrive(gauth)
    return drive

def upload_files_to_drive(local_path_name, drive_folder_name):
    drive = authenticate_google_drive()
    folder = drive.ListFile({'q': "title='" + drive_folder_name + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()[0]

    if folder:
        fileList = drive.ListFile({'q': "'"+ folder['id'] +"' in parents and trashed=false"}).GetList()
        if not fileList:
            for x in os.listdir(local_path_name):
                f = drive.CreateFile({'title': x, 'parents': [{'id': folder['id']}]})
                f.SetContentFile(os.path.join(local_path_name, x))
                f.Upload()
                print('1 new file upload is completed. File Name: {}'.format(x))
        else:
            fileTitleList = []
            for file in fileList:
                fileList = drive.ListFile({'q': "'"+ folder['id'] +"' in parents and trashed=false"}).GetList()
                for x in os.listdir(local_path_name):
                    for title in fileList:
                        fileTitleList.append(title['title'])
                    if x in fileTitleList and x == file['title']:
                        f = drive.CreateFile({'title': x, 'id': file['id'],'parents': [{'id': folder['id']}]})
                        f.SetContentFile(os.path.join(local_path_name, x))
                        f.Upload()
                        print('1 file that already exists is updated. File Name: {}'.format(x))
                    elif x not in fileTitleList:
                        f = drive.CreateFile({'title': x, 'parents': [{'id': folder['id']}]})
                        f.SetContentFile(os.path.join(local_path_name, x))
                        f.Upload()
                        print('1 new file upload is completed. File Name: {}'.format(x))
    else:
        print('The given folder name was not found in Google Drive. Please make sure the given folder name is correct.')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--drive", "-d",
                        type=str,
                        help="set google drive folder")
    parser.add_argument("--local", "-l",
                        type=str,
                        help="set local folder")
    args = parser.parse_args()
    
    local_path_name = args.local
    drive_folder_name = args.drive
    
    upload_files_to_drive(local_path_name, drive_folder_name)

if __name__== "__main__":
  main()