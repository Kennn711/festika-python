"""
File operations (copy, move, delete, rename, create)
"""
import shutil
from pathlib import Path


def copy_item(source_path, dest_dir):
    """Copy file atau folder ke directory tujuan"""
    try:
        source = Path(source_path)
        dest = Path(dest_dir) / source.name
        
        # Cek jika sudah ada
        if dest.exists():
            # Generate nama baru dengan suffix
            counter = 1
            while dest.exists():
                if source.is_dir():
                    dest = Path(dest_dir) / f"{source.name}_copy{counter}"
                else:
                    stem = source.stem
                    suffix = source.suffix
                    dest = Path(dest_dir) / f"{stem}_copy{counter}{suffix}"
                counter += 1
        
        if source.is_dir():
            shutil.copytree(source, dest)
        else:
            shutil.copy2(source, dest)
        
        return True, f"Copied to {dest.name}"
    except Exception as e:
        return False, f"Copy failed: {str(e)}"


def copy_multiple_items(source_paths, dest_dir):
    """Copy multiple files/folders ke directory tujuan"""
    success_count = 0
    failed_items = []
    
    for source_path in source_paths:
        success, msg = copy_item(source_path, dest_dir)
        if success:
            success_count += 1
        else:
            failed_items.append(Path(source_path).name)
    
    if failed_items:
        return True, f"Copied {success_count} items. Failed: {', '.join(failed_items)}"
    else:
        return True, f"Successfully copied {success_count} items"


def move_item(source_path, dest_dir):
    """Move file atau folder ke directory tujuan"""
    try:
        source = Path(source_path)
        dest = Path(dest_dir) / source.name
        
        # Cek jika sudah ada
        if dest.exists():
            return False, f"Item already exists: {dest.name}"
        
        shutil.move(source, dest)
        return True, f"Moved to {dest.name}"
    except Exception as e:
        return False, f"Move failed: {str(e)}"


def move_multiple_items(source_paths, dest_dir):
    """Move multiple files/folders ke directory tujuan"""
    success_count = 0
    failed_items = []
    
    for source_path in source_paths:
        success, msg = move_item(source_path, dest_dir)
        if success:
            success_count += 1
        else:
            failed_items.append(Path(source_path).name)
    
    if failed_items:
        return True, f"Moved {success_count} items. Failed: {', '.join(failed_items)}"
    else:
        return True, f"Successfully moved {success_count} items"


def delete_item(path):
    """Delete file atau folder"""
    try:
        path_obj = Path(path)
        
        if path_obj.is_dir():
            shutil.rmtree(path)
        else:
            path_obj.unlink()
        
        return True, "Deleted successfully"
    except Exception as e:
        return False, f"Delete failed: {str(e)}"


def delete_multiple_items(paths):
    """Delete multiple files/folders"""
    success_count = 0
    failed_items = []
    
    for path in paths:
        success, msg = delete_item(path)
        if success:
            success_count += 1
        else:
            failed_items.append(Path(path).name)
    
    if failed_items:
        return True, f"Deleted {success_count} items. Failed: {', '.join(failed_items)}"
    else:
        return True, f"Successfully deleted {success_count} items"


def rename_item(old_path, new_name):
    """Rename file atau folder"""
    try:
        old_path_obj = Path(old_path)
        new_path = old_path_obj.parent / new_name
        
        if new_path.exists():
            return False, f"Name already exists: {new_name}"
        
        old_path_obj.rename(new_path)
        return True, f"Renamed to {new_name}"
    except Exception as e:
        return False, f"Rename failed: {str(e)}"


def create_folder(parent_dir, folder_name):
    """Create folder baru"""
    try:
        new_folder = Path(parent_dir) / folder_name
        
        if new_folder.exists():
            return False, f"Folder already exists: {folder_name}"
        
        new_folder.mkdir(parents=True)
        return True, f"Created folder: {folder_name}"
    except Exception as e:
        return False, f"Create folder failed: {str(e)}"


def create_file(parent_dir, filename):
    """Create file baru (kosong)"""
    try:
        new_file = Path(parent_dir) / filename
        
        if new_file.exists():
            return False, f"File already exists: {filename}"
        
        # Buat file kosong
        new_file.touch()
        return True, f"Created file: {filename}"
    except Exception as e:
        return False, f"Create file failed: {str(e)}"