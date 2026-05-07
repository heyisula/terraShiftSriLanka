import os
import shutil
import re
from collections import defaultdict


SOURCE_DIR = "uncategorized"
TARGET_DIR = "data"

os.makedirs(TARGET_DIR, exist_ok=True)
pattern = re.compile(r"_(\d{8})_")

files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".TIF") or f.endswith(".txt") or f.endswith(".xml")]
grouped = defaultdict(list)

#Grouping files by the timeline
for file in files:
    match = pattern.search(file)
    if match:
        date = match.group(1)  # YYYYMMDD
        year_month = f"{date[:4]}_{date[4:6]}"
        grouped[year_month].append(file)

#Creating and diving into folders
for folder, file_list in grouped.items():
    folder_path = os.path.join(TARGET_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)

    for file in file_list:
        src = os.path.join(SOURCE_DIR, file)
        dst = os.path.join(folder_path, file)
        shutil.move(src, dst)
print("Files have been categorized and moved to respective folders.")