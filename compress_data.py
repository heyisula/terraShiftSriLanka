#!/usr/bin/env python3
"""
Landsat Raster Downscaler & GeoTIFF Compressor
==============================================
This script recursively scans the 'data' folder, resamples/downscales raster (.TIF)
files to a lower resolution (reducing size quadratically), applies high-performance
internal GeoTIFF compression, and replicates the layout in the 'compressed' folder.

Non-raster files (.txt, .xml) are copied directly to maintain complete directory consistency.
Uses multiprocessing to compress files in parallel across all CPU cores.
"""

import os
import sys
import time
import shutil
import concurrent.futures
from pathlib import Path

# Try importing rasterio
try:
    import rasterio
    from rasterio.enums import Resampling
except ImportError:
    print("Error: 'rasterio' is not installed in the current Python environment.")
    print("Please install it using: pip install rasterio")
    sys.exit(1)

# Configuration
SOURCE_DIR = Path("data")
TARGET_DIR = Path("compressed")

# Downscale factor (0.5 means width/height is reduced by 50%, i.e. 25% of the total pixel area)
# e.g., 30m resolution -> 60m resolution
SCALE_FACTOR = 0.5 

def format_size(bytes_size):
    """Formats bytes into human-readable sizes."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"

def compress_single_raster(task_info):
    """
    Downscales and internally compresses a single GeoTIFF file.
    Runs in a separate process.
    """
    src_path, dst_path = task_info
    try:
        # Create parent directories for the destination file
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        orig_size = src_path.stat().st_size
        start_time = time.time()
        
        # Open source GeoTIFF
        with rasterio.open(src_path) as src:
            # 1. Determine new resampled dimensions
            new_width = max(1, int(src.width * SCALE_FACTOR))
            new_height = max(1, int(src.height * SCALE_FACTOR))
            
            # 2. Select appropriate resampling algorithm
            # Mask / QA bands have discrete categories/bitmasks and MUST use Nearest Neighbor
            # to prevent intermediate values from being interpolated.
            # Spectral bands (SR_B1 to SR_B7) can use Bilinear for smooth transitions.
            is_qa_or_mask = "QA" in src_path.name or "mask" in src_path.name.lower()
            resampling_method = Resampling.nearest if is_qa_or_mask else Resampling.bilinear
            
            # 3. Read and resample the data
            data = src.read(
                out_shape=(src.count, new_height, new_width),
                resampling=resampling_method
            )
            
            # 4. Update the affine transform matrix for the new cell resolution
            transform = src.transform * src.transform.scale(
                (src.width / new_width),
                (src.height / new_height)
            )
            
            # 5. Build optimized compression profile
            profile = src.profile.copy()
            
            # Choose optimal spatial predictor (highly effective for increasing compression ratios)
            # Predictor=2 is horizontal difference for integers; Predictor=3 is for floating points
            dtype_name = src.dtypes[0]
            if "int" in dtype_name:
                predictor = 2
            elif "float" in dtype_name:
                predictor = 3
            else:
                predictor = 1  # No predictor
                
            profile.update({
                'height': new_height,
                'width': new_width,
                'transform': transform,
                'compress': 'deflate',  # High efficiency standard compression
                'compresslevel': 6,     # Level 6 is the sweet spot for deflate speed/ratio
                'predictor': predictor,
                'tiled': True,
                'blockxsize': min(256, new_width),
                'blockysize': min(256, new_height)
            })
            
            # Write optimized raster
            with rasterio.open(dst_path, 'w', **profile) as dst:
                dst.write(data)
                
        comp_size = dst_path.stat().st_size
        duration = time.time() - start_time
        
        return {
            "success": True,
            "type": "raster",
            "src": str(src_path),
            "dst": str(dst_path),
            "orig_size": orig_size,
            "comp_size": comp_size,
            "duration": duration,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "type": "raster",
            "src": str(src_path),
            "dst": str(dst_path),
            "orig_size": 0,
            "comp_size": 0,
            "duration": 0,
            "error": str(e)
        }

def copy_metadata_file(task_info):
    """Copies non-raster metadata files directly to target."""
    src_path, dst_path = task_info
    try:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        orig_size = src_path.stat().st_size
        
        # Copy file
        shutil.copy2(src_path, dst_path)
        
        comp_size = dst_path.stat().st_size
        return {
            "success": True,
            "type": "metadata",
            "src": str(src_path),
            "dst": str(dst_path),
            "orig_size": orig_size,
            "comp_size": comp_size,
            "duration": 0,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "type": "metadata",
            "src": str(src_path),
            "dst": str(dst_path),
            "orig_size": 0,
            "comp_size": 0,
            "duration": 0,
            "error": str(e)
        }

def show_progress_bar(completed, total, bar_length=40):
    """Displays a clean console progress bar."""
    if total == 0:
        return
    percent = float(completed) / total
    filled_len = int(round(percent * bar_length))
    arrow = '#' * filled_len
    spaces = '-' * (bar_length - filled_len)
    
    sys.stdout.write(f"\rProgress: [{arrow}{spaces}] {completed}/{total} files ({percent*100:.1f}%)")
    sys.stdout.flush()

def main():
    print("=" * 60)
    print("      Landsat Raster Downscaler & GeoTIFF Compressor")
    print("=" * 60)
    print(f"Scale Factor:   {SCALE_FACTOR} (Width/Height reduced by 50% -> Area by 75%)")
    print(f"Source Folder:  '{SOURCE_DIR}'")
    print(f"Target Folder:  '{TARGET_DIR}'")
    print("-" * 60)
    
    if not SOURCE_DIR.exists():
        print(f"Error: Source directory '{SOURCE_DIR}' does not exist.")
        sys.exit(1)
        
    print("Scanning source directory for files...")
    
    raster_tasks = []
    metadata_tasks = []
    
    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            src_file = Path(root) / file
            rel_path = src_file.relative_to(SOURCE_DIR)
            dst_file = TARGET_DIR / rel_path
            
            # Separate TIF rasters from other metadata files (txt, xml)
            if src_file.suffix.lower() in [".tif", ".tiff"]:
                raster_tasks.append((src_file, dst_file))
            else:
                metadata_tasks.append((src_file, dst_file))
                
    total_rasters = len(raster_tasks)
    total_metadata = len(metadata_tasks)
    total_files = total_rasters + total_metadata
    
    if total_files == 0:
        print("No files found to process.")
        sys.exit(0)
        
    print(f"Found {total_files} files in total:")
    print(f" - {total_rasters} GeoTIFF rasters (.TIF) to downscale & compress")
    print(f" - {total_metadata} metadata files (.txt, .xml) to copy as-is")
    print("-" * 60)
    
    # Process metadata files first (very fast copy)
    print("1. Processing metadata files...")
    total_orig_size = 0
    total_comp_size = 0
    completed_count = 0
    failed_count = 0
    failed_files = []
    
    for task in metadata_tasks:
        res = copy_metadata_file(task)
        if res["success"]:
            total_orig_size += res["orig_size"]
            total_comp_size += res["comp_size"]
        else:
            failed_count += 1
            failed_files.append((res["src"], res["error"]))
        completed_count += 1
        show_progress_bar(completed_count, total_files)
        
    print(f"\nMetadata copy finished. Handled {total_metadata} files.")
    print("-" * 60)
    
    # Process rasters in parallel
    print("2. Starting parallel raster downscaling and compression...")
    start_time = time.time()
    
    max_workers = os.cpu_count() or 4
    print(f"Spawning {max_workers} worker processes for CPU-bound resampling...")
    
    # Show initial progress with completed metadata
    show_progress_bar(completed_count, total_files)
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit raster downscale tasks to process pool
        future_to_raster = {executor.submit(compress_single_raster, task): task for task in raster_tasks}
        
        for future in concurrent.futures.as_completed(future_to_raster):
            result = future.result()
            completed_count += 1
            
            if result["success"]:
                total_orig_size += result["orig_size"]
                total_comp_size += result["comp_size"]
            else:
                failed_count += 1
                failed_files.append((result["src"], result["error"]))
                
            # Update console progress bar
            show_progress_bar(completed_count, total_files)
            
    total_duration = time.time() - start_time
    print("\n" + "-" * 60)
    print("Process complete!")
    print("=" * 60)
    print("                       SUMMARY REPORT")
    print("=" * 60)
    print(f"Time Taken:            {total_duration:.2f} seconds")
    print(f"Files Processed:       {completed_count - failed_count} / {total_files}")
    
    if failed_count > 0:
        print(f"Files Failed:          {failed_count}")
        print("\nErrors encountered:")
        for src, err in failed_files:
            print(f" - {src}: {err}")
        print("-" * 60)
        
    if completed_count - failed_count > 0:
        saved_bytes = total_orig_size - total_comp_size
        savings_pct = (saved_bytes / total_orig_size * 100) if total_orig_size > 0 else 0
        
        print(f"Original Size:         {format_size(total_orig_size)}")
        print(f"Compressed Size:       {format_size(total_comp_size)}")
        print(f"Total Disk Space Saved: {format_size(saved_bytes)} ({savings_pct:.1f}% reduction!)")
        print("\nNote: GeoTIFF metadata & coordinate reference systems have been fully preserved.")
        print("Your classification pipeline can use the 'compressed' folder directly.")
    print("=" * 60)

if __name__ == "__main__":
    main()
