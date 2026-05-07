import os
folder_path = r"uncategorized"
output_file = "landsat_filenames.txt"

files = os.listdir(folder_path)

with open(output_file, "w") as f:
    for file in files:
        f.write(file + "\n")

print(f"Saved {len(files)} filenames to {output_file}")