# import requests
# import os


# def download_file(url, save_path):
#     response = requests.get(url, stream=True)
#     response.raise_for_status()
#     with open(save_path, "wb") as file:
#         for chunk in response.iter_content(chunk_size=8192):
#             file.write(chunk)


# def download_zarr(url, save_folder):
#     # Пути к основным компонентам Zarr-архива
#     paths = ["", "/.zgroup", "/.zarray", "/.zattrs"]

#     for path in paths:
#         full_url = url + path
#         save_path = os.path.join(save_folder, path.lstrip("/"))
#         os.makedirs(os.path.dirname(save_path), exist_ok=True)
#         print(f"Downloading {full_url} to {save_path}")
#         download_file(full_url, save_path)


# # URL к корню Zarr-архива
# url = "https://s3.amazonaws.com/vitessce-data/0.0.33/main/kuppe-2022/kuppe_2022_nature.visium.h5ad.zarr"
# save_folder = "C:\\temp\\234"

# download_zarr(url, save_folder)


# import zarr

# # Открываем Zarr хранилище
# root = zarr.open("C:\\temp\\234\kuppe_2022_nature.visium.ome.zarr", mode="r")

# # Просмотрим корневую структуру
# print("Корневая структура:")
# print(root.info)


# # Проходимся по всем группам и массивам для просмотра их структуры и метаданных
# def explore_group(group, indent=0):
#     indent_str = " " * indent
#     for name, array in group.arrays():
#         print(f"{indent_str}- {name} (array)")
#         print(f"{indent_str}  {array.info}")
#     for name, subgroup in group.groups():
#         print(f"{indent_str}- {name} (group)")
#         explore_group(subgroup, indent=indent + 2)


# print("Детальная структура и метаданные:")
# explore_group(root)


# import boto3
# import botocore
# import os

# # Используем анонимный доступ
# s3_client = boto3.client(
#     "s3", config=botocore.client.Config(signature_version=botocore.UNSIGNED)
# )

# # Задаем имя бакета и префикс пути
# bucket_name = "vitessce-data"
# prefix = "0.0.33/main/kuppe-2022/kuppe_2022_nature.visium.h5ad.zarr"

# # Задаем локальный путь для сохранения файлов
# local_path = "C:\\temp\\234\\kuppe_2022_nature.visium.h5ad.zarr"

# # Создаем локальную папку, если ее еще нет
# os.makedirs(local_path, exist_ok=True)

# # Получаем список всех объектов в бакете с заданным префиксом
# result = s3_client.list_objects(Bucket=bucket_name, Prefix=prefix)

# # Проходим по всем объектам и скачиваем их
# for item in result.get("Contents", []):
#     file_name = item["Key"]
#     if not file_name.endswith("/"):  # Пропускаем пустые "папки"
#         file_path = os.path.join(local_path, os.path.relpath(file_name, prefix))
#         file_dir = os.path.dirname(file_path)

#         # Создаем локальные папки, если их еще нет
#         os.makedirs(file_dir, exist_ok=True)

#         # Скачиваем файл
#         print(f"Downloading {file_name} to {file_path}")

#         s3_client.download_file(bucket_name, file_name, file_path)


import zarr


def list_keys_and_print_selected(group, prefix="", selected_paths=[]):
    # print(1)
    # group.obsm["xy_segmentations_scaled"]
    # print(1)
    for key in group.keys():
        new_key = f"{prefix}/{key}" if prefix else key
        full_key = f"{prefix}/{key}" if prefix else key  # Полный путь до ключа
        if isinstance(group[key], zarr.Group):
            list_keys_and_print_selected(group[key], new_key, selected_paths)
        else:
            if full_key in selected_paths:
                print(f"Key: {full_key}")
                data = group[key][:]
                print(f"First 10 records of {full_key}: {data[:3]}")


# Ваш код остается без изменений
root = zarr.open_group("c:\\temp\\234\\kuppe_2022_nature.visium.h5ad.zarr", mode="r")
selected_paths = [
    "obsm/xy_scaled",
    "obsm/xy_segmentations_scaled",
    # "X",
    # "var/feature_name",
]
list_keys_and_print_selected(root, selected_paths=selected_paths)
