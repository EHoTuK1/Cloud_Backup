from abc import ABC, abstractmethod

class CloudStorage(ABC):
    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Загрузка файла на облачное хранилище"""
        pass

    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Скачивание файла с облачного хранилища"""
        pass

    @abstractmethod
    def create_folder(self, path: str) -> bool:
        """Создание папки в облачном хранилище"""
        pass

    @abstractmethod
    def delete_file_or_folder(self, path: str, permanently: bool = False) -> bool:
        """Удаление файла или папки из облачного хранилища"""
        pass

    @abstractmethod
    def list_files(self, path: str) -> list:
        """Получение списка файлов в указанной директории"""
        pass