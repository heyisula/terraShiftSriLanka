import os
folder_path = r"data/"

# Output text file
output_file = "landsat_filenames.txt"

# Get all filenames
files = os.listdir(folder_path)

# Save filenames to text file
with open(output_file, "w") as f:
    for file in files:
        f.write(file + "\n")

print(f"Saved {len(files)} filenames to {output_file}")