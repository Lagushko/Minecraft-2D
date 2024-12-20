import os
import json
import shutil

sound_names = ["wood/"]
index_file = r"C:/Users/march/AppData/Roaming/.minecraft/assets/indexes/5.json"
objects_folder = r"C:/Users/march/AppData/Roaming/.minecraft/assets/objects/"
out_folder = os.path.dirname(os.path.abspath(__file__))
target_folder = os.path.join(out_folder)

if not os.path.exists(index_file):
    raise FileNotFoundError(f"Не найден файл индекса: {index_file}")
if not os.path.exists(objects_folder):
    raise FileNotFoundError(f"Не найдена папка объектов: {objects_folder}")

with open(index_file, "r", encoding="utf-8") as f:
    index_data = json.load(f)

for sound_name in sound_names:
    found = False
    for key, value in index_data.get("objects", {}).items():
        if key.startswith("minecraft/sounds") and sound_name in key:
            hash_code = value["hash"]
            subfolder = hash_code[:2]
            hash_file = os.path.join(objects_folder, subfolder, hash_code)

            if os.path.exists(hash_file):
                output_name = os.path.basename(key)
                if not os.path.exists(os.path.join(target_folder, output_name)):
                    output_path = os.path.join(target_folder, output_name)
                    shutil.copy(hash_file, output_path)
                    print(f"Найден и сохранен: {key} -> {output_path}")
                    found = True
    if not found:
        print(f"Не удалось найти звук: {sound_name}")

print("Готово!")
