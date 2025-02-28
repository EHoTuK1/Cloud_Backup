from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import os.path
import pickle
from typing import List
from CloudStorage import CloudStorage

class GoogleDrive(CloudStorage):
    """
    Реализация CloudStorage для Google Drive.
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']

    def __init__(self):
        self.service = self._get_service()

    def _get_service(self):
        """Получает службу Google Drive API."""
        creds = None
        token_path = 'token.pickle'

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('drive', 'v3', credentials=creds)

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Загружает локальный файл на Google Drive."""
        file_metadata = {'name': os.path.basename(remote_path)}
        media = MediaFileUpload(local_path, resumable=True)
        try:
            self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"Файл {local_path} успешно загружен.")
            return True
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Скачивает файл с Google Drive на локальную машину."""
        file_id = self._get_file_id_by_path(remote_path)
        if not file_id:
            print(f"Файл {remote_path} не найден.")
            return False

        request = self.service.files().get_media(fileId=file_id)
        with open(local_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Скачивание {int(status.progress() * 100)}% завершено.")
        print(f"Файл {remote_path} успешно скачан.")
        return True

    def create_folder(self, path: str) -> bool:
        """Создает папку в Google Drive."""
        folder_name = os.path.basename(path)
        parent_id = self._get_parent_id_by_path(os.path.dirname(path))

        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]

        try:
            self.service.files().create(body=file_metadata, fields='id').execute()
            print(f"Папка {path} успешно создана.")
            return True
        except Exception as e:
            print(f"Ошибка создания папки: {e}")
            return False

    def delete_file_or_folder(self, path: str) -> bool:
        """Удаляет файл или папку из Google Drive."""
        file_id = self._get_file_id_by_path(path)
        if not file_id:
            print(f"Файл/папка {path} не найдена.")
            return False

        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"Файл/папка {path} успешно удалена.")
            return True
        except Exception as e:
            print(f"Ошибка удаления: {e}")
            return False

    def list_files(self, path: str) -> List[str]:
        """Возвращает список файлов в указанной директории."""
        parent_id = self._get_parent_id_by_path(path)
        if not parent_id:
            print(f"Директория {path} не найдена.")
            return []

        query = f"'{parent_id}' in parents and trashed=false"
        results = self.service.files().list(q=query, fields="files(name)").execute()
        files = results.get('files', [])
        print(f"Список файлов в {path}: {files}")
        return [file['name'] for file in files]

    def _get_file_id_by_path(self, path: str) -> str:
        """Вспомогательный метод для получения ID файла по пути."""
        parts = path.strip('/').split('/')
        current_id = 'root'
        for part in parts:
            query = f"'{current_id}' in parents and name='{part}' and trashed=false"
            result = self.service.files().list(q=query, fields="files(id)").execute()
            files = result.get('files', [])
            if not files:
                return None
            current_id = files[0]['id']
        return current_id

    def _get_parent_id_by_path(self, path: str) -> str:
        """Вспомогательный метод для получения ID родительской папки по пути."""
        if not path or path == '/':
            return 'root'
        return self._get_file_id_by_path(path)