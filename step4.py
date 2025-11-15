import msvcrt
import os
import shutil
from pathlib import Path
from datetime import datetime
import subprocess

# ============================================
# KEYBOARD INPUT
# ============================================
def get_key():
    """Fungsi untuk menangkap input keyboard"""
    key = msvcrt.getch()
    
    # Arrow keys di Windows return 2 bytes
    if key == b'\xe0':  # Special key prefix
        key = msvcrt.getch()
        if key == b'H':    # Up arrow
            return 'UP'
        elif key == b'P':  # Down arrow
            return 'DOWN'
        elif key == b'K':  # Left arrow
            return 'LEFT'
        elif key == b'M':  # Right arrow
            return 'RIGHT'
    elif key == b'\r':     # Enter
        return 'ENTER'
    elif key == b'q' or key == b'Q':  # Quit
        return 'QUIT'
    
    return None

# ============================================
# SCREEN & UI RENDERING
# ============================================
def clear_screen():
    """Clear terminal screen (Windows)"""
    os.system('cls')

def get_terminal_size():
    """Get ukuran terminal (columns, lines)"""
    size = shutil.get_terminal_size()
    return size.columns, size.lines

def draw_header(current_path):
    """Gambar header dengan path saat ini"""
    cols, _ = get_terminal_size()
    
    # Header border
    print("┌" + "─" * (cols - 2) + "┐")
    
    # Path info
    path_text = f" Current Path: {current_path} "
    # Potong jika terlalu panjang
    if len(path_text) > cols - 2:
        path_text = path_text[:cols-5] + "..."
    
    padding = cols - len(path_text) - 2
    print("│" + path_text + " " * padding + "│")
    
    # Separator
    print("├" + "─" * (cols - 2) + "┤")

def draw_footer():
    """Gambar footer dengan help commands"""
    cols, _ = get_terminal_size()
    
    help_text = " [↑↓: Navigate | Enter: Open | Q: Quit] "
    padding = cols - len(help_text) - 2
    
    print("└" + "─" * (cols - 2) + "┘")
    print(help_text.center(cols))

# ============================================
# FILE SYSTEM OPERATIONS
# ============================================
def format_size(size_bytes):
    """Convert bytes ke format human-readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def get_file_info(path):
    """Get informasi file (ukuran, tanggal modifikasi)"""
    try:
        stat = path.stat()
        size = format_size(stat.st_size)
        modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        return size, modified
    except:
        return "N/A", "N/A"

def scan_directory(path):
    """
    Scan directory dan return list items dengan format:
    (name, is_dir, size, modified, full_path)
    """
    items = []
    
    try:
        path_obj = Path(path)
        
        # Tambahkan ".." untuk naik ke parent (kecuali di root)
        if path_obj.parent != path_obj:
            items.append(("..", True, "", "", str(path_obj.parent)))
        
        # Scan semua item di directory
        for item in path_obj.iterdir():
            try:
                is_dir = item.is_dir()
                
                if is_dir:
                    # Folder: tidak perlu size
                    items.append((item.name, True, "", "", str(item)))
                else:
                    # File: ambil size dan modified date
                    size, modified = get_file_info(item)
                    items.append((item.name, False, size, modified, str(item)))
            except PermissionError:
                # Skip file/folder yang tidak bisa diakses
                continue
        
        # Sort: folder dulu, baru file (alphabetically)
        items.sort(key=lambda x: (not x[1], x[0].lower()))
        
    except PermissionError:
        return [("Permission Denied", False, "", "", "")]
    except Exception as e:
        return [(f"Error: {str(e)}", False, "", "", "")]
    
    return items

def format_item_display(item, max_width):
    """Format item untuk ditampilkan di UI"""
    name, is_dir, size, modified, _ = item
    
    # Icon
    icon = "📁" if is_dir else "📄"
    
    # Format display berdasarkan tipe
    if is_dir:
        display = f"{icon} {name}/"
    else:
        # File dengan info size
        display = f"{icon} {name}"
        # Padding untuk align size di kanan
        padding_size = max_width - len(display) - len(size) - 4
        if padding_size > 0:
            display += " " * padding_size + size
    
    return display

def open_file(filepath):
    """Open file dengan aplikasi default Windows"""
    try:
        os.startfile(filepath)
        return True
    except Exception as e:
        return False

def change_directory(new_path):
    """Pindah ke directory baru dan return items"""
    try:
        # Validasi path exists
        if os.path.exists(new_path) and os.path.isdir(new_path):
            return new_path, scan_directory(new_path)
        else:
            return None, []
    except:
        return None, []

# ============================================
# UI RENDERING
# ============================================
def render_ui(current_path, items, selected_index, message=""):
    """Render UI dengan data real"""
    clear_screen()
    
    cols, lines = get_terminal_size()
    
    # Header
    draw_header(current_path)
    
    # Message (jika ada)
    if message:
        print(f" ⓘ {message}")
        print()
    
    # Calculate max displayable items (minus header/footer)
    max_display = lines - 10 if message else lines - 8
    
    # File list
    for idx, item in enumerate(items[:max_display]):
        display_text = format_item_display(item, cols - 6)
        
        if idx == selected_index:
            # Item yang dipilih
            print(f" > {display_text}")
        else:
            print(f"   {display_text}")
    
    # Info jika ada lebih banyak items
    if len(items) > max_display:
        print(f"\n   ... and {len(items) - max_display} more items")
    
    # Footer
    print()
    draw_footer()

# ============================================
# MAIN PROGRAM
# ============================================
def main():
    # Start dari current directory
    current_path = os.getcwd()
    selected = 0
    message = ""
    
    # Scan directory pertama kali
    items = scan_directory(current_path)
    
    # Render pertama
    render_ui(current_path, items, selected, message)
    
    while True:
        key = get_key()
        message = ""  # Reset message
        
        if key == 'UP':
            selected = max(0, selected - 1)
            render_ui(current_path, items, selected, message)
            
        elif key == 'DOWN':
            selected = min(len(items) - 1, selected + 1)
            render_ui(current_path, items, selected, message)
            
        elif key == 'ENTER':
            if items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                
                if is_dir:
                    # Masuk ke folder
                    new_path, new_items = change_directory(full_path)
                    if new_path:
                        current_path = new_path
                        items = new_items
                        selected = 0
                        message = f"Opened: {name}"
                    else:
                        message = f"Cannot access: {name}"
                else:
                    # Open file dengan aplikasi default
                    if open_file(full_path):
                        message = f"Opening: {name}"
                    else:
                        message = f"Cannot open: {name}"
                
                render_ui(current_path, items, selected, message)
            
        elif key == 'QUIT':
            clear_screen()
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()