import os
from GDrive import GoogleDrive

# Создаем экземпляр класса
drive = GoogleDrive()

# Путь к тестовому файлу
local_file = "test_upload.txt"
with open(local_file, "w") as f:
    f.write("Этот файл создан для тестирования загрузки на Google Drive.")

# Загрузить файл в корень Google Drive
remote_file = "test_upload.txt"
drive.upload_file(local_file, remote_file)
input()
# Создать папку
folder_name = "TestFolder"
drive.create_folder(folder_name)
input()
# Создать вложенные папки
nested_folder = "TestFolder/NestedFolder"
drive.create_folder(nested_folder)
input()
# Переместить загруженный файл в вложенную папку
nested_remote_path = "TestFolder/NestedFolder/test_upload.txt"
file_id = drive._get_file_id_by_path(remote_file)
folder_id = drive._get_file_id_by_path(nested_folder)
input()
if file_id and folder_id:
    drive.service.files().update(fileId=file_id, addParents=folder_id, removeParents='root').execute()
    print(f"Файл перемещен в {nested_remote_path}")
input()
# Скачать файл обратно
download_path = "downloaded_test_upload.txt"
drive.download_file(nested_remote_path, download_path)
input()
# Удалить файл и папки
drive.delete_file_or_folder(nested_remote_path)
drive.delete_file_or_folder(nested_folder)
drive.delete_file_or_folder(folder_name)
input()
print("Тест завершен успешно!")

