"""
Compression and extraction functions
"""
import zipfile
import tarfile
import subprocess
from pathlib import Path
import os


def is_archive(filename):
    """Check if file is an archive"""
    archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.tar.gz', '.tar.bz2', '.tar.xz']
    return any(filename.lower().endswith(ext) for ext in archive_extensions)


def compress_to_zip(source_paths, output_path):
    """Compress files/folders to ZIP"""
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for source_path in source_paths:
                source = Path(source_path)
                
                if source.is_file():
                    # Add file
                    zipf.write(source, source.name)
                elif source.is_dir():
                    # Add directory recursively
                    for file_path in source.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source.parent)
                            zipf.write(file_path, arcname)
        
        return True, f"Successfully compressed to {Path(output_path).name}"
    except Exception as e:
        return False, f"ZIP compression failed: {str(e)}"


def compress_to_7z(source_paths, output_path):
    """Compress files/folders to 7Z using 7-Zip"""
    try:
        # Try to find 7z.exe in common locations
        possible_paths = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe",
        ]
        
        seven_zip_path = None
        for path in possible_paths:
            if os.path.exists(path):
                seven_zip_path = path
                break
        
        if not seven_zip_path:
            return False, "7-Zip not found. Please install 7-Zip first."
        
        # Build command
        cmd = [seven_zip_path, 'a', '-t7z', output_path]
        cmd.extend(source_paths)
        
        # Execute
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, f"Successfully compressed to {Path(output_path).name}"
        else:
            return False, f"7Z compression failed: {result.stderr}"
    
    except Exception as e:
        return False, f"7Z compression failed: {str(e)}"


def compress_to_rar(source_paths, output_path):
    """Compress files/folders to RAR using WinRAR"""
    try:
        # Try to find WinRAR.exe in common locations
        possible_paths = [
            r"C:\Program Files\WinRAR\WinRAR.exe",
            r"C:\Program Files (x86)\WinRAR\WinRAR.exe",
        ]
        
        winrar_path = None
        for path in possible_paths:
            if os.path.exists(path):
                winrar_path = path
                break
        
        if not winrar_path:
            return False, "WinRAR not found. Please install WinRAR first."
        
        # Build command
        cmd = [winrar_path, 'a', '-ep1', output_path]
        cmd.extend(source_paths)
        
        # Execute
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, f"Successfully compressed to {Path(output_path).name}"
        else:
            return False, f"RAR compression failed"
    
    except Exception as e:
        return False, f"RAR compression failed: {str(e)}"


def extract_zip(archive_path, dest_dir):
    """Extract ZIP archive"""
    try:
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(dest_dir)
        
        return True, f"Successfully extracted {Path(archive_path).name}"
    except Exception as e:
        return False, f"ZIP extraction failed: {str(e)}"


def extract_7z(archive_path, dest_dir):
    """Extract 7Z archive using 7-Zip"""
    try:
        # Try to find 7z.exe
        possible_paths = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe",
        ]
        
        seven_zip_path = None
        for path in possible_paths:
            if os.path.exists(path):
                seven_zip_path = path
                break
        
        if not seven_zip_path:
            return False, "7-Zip not found. Please install 7-Zip first."
        
        # Build command
        cmd = [seven_zip_path, 'x', archive_path, f'-o{dest_dir}', '-y']
        
        # Execute
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, f"Successfully extracted {Path(archive_path).name}"
        else:
            return False, f"7Z extraction failed: {result.stderr}"
    
    except Exception as e:
        return False, f"7Z extraction failed: {str(e)}"


def extract_rar(archive_path, dest_dir):
    """Extract RAR archive using WinRAR"""
    try:
        # Try to find WinRAR.exe or UnRAR.exe
        possible_paths = [
            r"C:\Program Files\WinRAR\WinRAR.exe",
            r"C:\Program Files (x86)\WinRAR\WinRAR.exe",
            r"C:\Program Files\WinRAR\UnRAR.exe",
            r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
        ]
        
        winrar_path = None
        for path in possible_paths:
            if os.path.exists(path):
                winrar_path = path
                break
        
        if not winrar_path:
            return False, "WinRAR not found. Please install WinRAR first."
        
        # Build command
        cmd = [winrar_path, 'x', '-y', archive_path, dest_dir]
        
        # Execute
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, f"Successfully extracted {Path(archive_path).name}"
        else:
            return False, f"RAR extraction failed"
    
    except Exception as e:
        return False, f"RAR extraction failed: {str(e)}"


def extract_archive(archive_path, dest_dir):
    """Auto-detect and extract archive"""
    archive_path = Path(archive_path)
    ext = archive_path.suffix.lower()
    
    if ext == '.zip':
        return extract_zip(str(archive_path), dest_dir)
    elif ext == '.7z':
        return extract_7z(str(archive_path), dest_dir)
    elif ext == '.rar':
        return extract_rar(str(archive_path), dest_dir)
    else:
        # Try with 7-Zip as it supports many formats
        return extract_7z(str(archive_path), dest_dir)


def show_compression_menu(current_path, filter_ext):
    """Show compression format selection menu"""
    import msvcrt
    from .ui import clear_screen, draw_header, get_terminal_size
    
    clear_screen()
    cols, _ = get_terminal_size()
    
    draw_header(current_path, filter_ext=filter_ext)
    
    print("\n 📦 Compression Format")
    print(" " + "─" * 40)
    print("   [1] ZIP  (Built-in, no external tool needed)")
    print("   [2] 7Z   (Requires 7-Zip)")
    print("   [3] RAR  (Requires WinRAR)")
    print("\n " + "─" * 40)
    print(" [ESC] Cancel")
    
    while True:
        key = msvcrt.getch()
        
        if key == b'1':
            return 'zip', False
        elif key == b'2':
            return '7z', False
        elif key == b'3':
            return 'rar', False
        elif key == b'\x1b':  # ESC
            return None, True