<<<<<<< HEAD
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
    elif key == b'\x08':   # Backspace
        return 'BACKSPACE'
    elif key == b'/':      # Slash untuk search
        return 'SEARCH'
    elif key == b'f' or key == b'F':  # Filter
        return 'FILTER'
    elif key == b'q' or key == b'Q':  # Quit
        return 'QUIT'
    elif key == b'\x1b':   # ESC
        return 'ESC'
    
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

def draw_header(current_path, search_mode=False, search_query="", filter_ext=""):
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
    
    # Search/Filter info
    if search_mode:
        search_text = f" 🔍 Search: {search_query}_"
        padding = cols - len(search_text) - 2
        print("│" + search_text + " " * padding + "│")
    elif filter_ext:
        filter_text = f" 🔍 Filter: *.{filter_ext}"
        padding = cols - len(filter_text) - 2
        print("│" + filter_text + " " * padding + "│")
    
    # Separator
    print("├" + "─" * (cols - 2) + "┤")

def draw_footer(search_mode=False):
    """Gambar footer dengan help commands"""
    cols, _ = get_terminal_size()
    
    if search_mode:
        help_text = " [Type to search | Enter: Confirm | ESC: Cancel] "
    else:
        help_text = " [↑↓: Navigate | Enter: Open | /: Search | F: Filter | Backspace: Parent | Q: Quit] "
    
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

def search_items(items, query):
    """Filter items berdasarkan search query"""
    if not query:
        return items
    
    query_lower = query.lower()
    filtered = []
    
    # Keep ".." jika ada
    if items and items[0][0] == "..":
        filtered.append(items[0])
    
    # Filter items yang mengandung query
    for item in items:
        name = item[0]
        if name != ".." and query_lower in name.lower():
            filtered.append(item)
    
    return filtered

def filter_by_extension(items, extension):
    """Filter items berdasarkan extension"""
    if not extension:
        return items
    
    ext_lower = extension.lower()
    filtered = []
    
    # Keep ".." dan folders
    for item in items:
        name, is_dir, size, modified, full_path = item
        if name == ".." or is_dir:
            filtered.append(item)
        elif name.lower().endswith(f".{ext_lower}"):
            filtered.append(item)
    
    return filtered

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

def go_to_parent(current_path):
    """Naik ke parent directory"""
    parent_path = str(Path(current_path).parent)
    # Cek jika sudah di root
    if parent_path != current_path:
        return change_directory(parent_path)
    return None, []

# ============================================
# SEARCH MODE
# ============================================
def handle_search_input():
    """Handle input untuk search mode"""
    query = ""
    
    while True:
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter - confirm search
            return query, False
        elif key == b'\x1b':  # ESC - cancel search
            return "", True
        elif key == b'\x08':  # Backspace - hapus karakter
            if query:
                query = query[:-1]
        elif key == b'\xe0':  # Skip special keys (arrows)
            msvcrt.getch()  # Consume second byte
            continue
        else:
            # Tambah karakter (hanya alphanumeric dan beberapa simbol)
            try:
                char = key.decode('utf-8')
                if char.isprintable() and char not in ['\r', '\n']:
                    query += char
            except:
                continue
        
        # Return query untuk live update
        yield query

def handle_filter_input():
    """Handle input untuk filter extension"""
    extension = ""
    
    while True:
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter - confirm filter
            return extension, False
        elif key == b'\x1b':  # ESC - cancel filter
            return "", True
        elif key == b'\x08':  # Backspace - hapus karakter
            if extension:
                extension = extension[:-1]
        elif key == b'\xe0':  # Skip special keys
            msvcrt.getch()
            continue
        else:
            # Tambah karakter
            try:
                char = key.decode('utf-8')
                if char.isalnum() or char == '.':
                    extension += char
            except:
                continue
        
        yield extension

# ============================================
# UI RENDERING
# ============================================
def render_ui(current_path, items, selected_index, message="", search_mode=False, search_query="", filter_ext=""):
    """Render UI dengan data real"""
    clear_screen()
    
    cols, lines = get_terminal_size()
    
    # Header
    draw_header(current_path, search_mode, search_query, filter_ext)
    
    # Message (jika ada)
    if message:
        print(f" ⓘ {message}")
        print()
    
    # Calculate max displayable items (minus header/footer)
    extra_lines = 0
    if message:
        extra_lines += 2
    if search_mode or filter_ext:
        extra_lines += 1
    
    max_display = lines - 8 - extra_lines
    
    # File list
    if not items:
        print("   (No items found)")
    else:
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
    draw_footer(search_mode)

# ============================================
# MAIN PROGRAM
# ============================================
def main():
    # Start dari current directory
    current_path = os.getcwd()
    selected = 0
    message = ""
    filter_ext = ""
    
    # Scan directory pertama kali
    all_items = scan_directory(current_path)
    items = all_items
    
    # Render pertama
    render_ui(current_path, items, selected, message, filter_ext=filter_ext)
    
    while True:
        key = get_key()
        message = ""  # Reset message
        
        if key == 'UP':
            selected = max(0, selected - 1)
            render_ui(current_path, items, selected, message, filter_ext=filter_ext)
            
        elif key == 'DOWN':
            selected = min(len(items) - 1, selected + 1) if items else 0
            render_ui(current_path, items, selected, message, filter_ext=filter_ext)
            
        elif key == 'BACKSPACE':
            # Naik ke parent directory
            new_path, new_items = go_to_parent(current_path)
            if new_path:
                current_path = new_path
                all_items = new_items
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                selected = 0
                message = "Moved to parent directory"
            else:
                message = "Already at root directory"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext)
            
        elif key == 'ENTER':
            if items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                
                if is_dir:
                    # Masuk ke folder
                    new_path, new_items = change_directory(full_path)
                    if new_path:
                        current_path = new_path
                        all_items = new_items
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
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
                
                render_ui(current_path, items, selected, message, filter_ext=filter_ext)
        
        elif key == 'SEARCH':
            # Search mode
            search_query = ""
            for query in handle_search_input():
                search_query = query
                temp_items = search_items(all_items, search_query)
                render_ui(current_path, temp_items, 0, f"Searching: {len(temp_items)} results", 
                         search_mode=True, search_query=search_query, filter_ext=filter_ext)
            
            # After search confirmed or cancelled
            if search_query:
                items = search_items(all_items, search_query)
                selected = 0
                message = f"Search results: {len(items)} items found"
            else:
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext)
        
        elif key == 'FILTER':
            # Filter mode
            temp_ext = ""
            for ext in handle_filter_input():
                temp_ext = ext.lstrip('.')  # Remove leading dot if any
                temp_items = filter_by_extension(all_items, temp_ext)
                render_ui(current_path, temp_items, 0, f"Filter: *.{temp_ext} ({len(temp_items)} items)", 
                         search_mode=True, search_query=temp_ext, filter_ext=temp_ext)
            
            # After filter confirmed or cancelled
            filter_ext = temp_ext
            if filter_ext:
                items = filter_by_extension(all_items, filter_ext)
                selected = 0
                message = f"Filtered by *.{filter_ext}: {len(items)} items"
            else:
                items = all_items
                message = "Filter cleared"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext)
            
        elif key == 'ESC':
            # Clear search/filter
            filter_ext = ""
            items = all_items
            selected = 0
            message = "Filter cleared"
            render_ui(current_path, items, selected, message)
            
        elif key == 'QUIT':
            clear_screen()
            print("Goodbye!")
            break

if __name__ == "__main__":
=======
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
    elif key == b'\x08':   # Backspace
        return 'BACKSPACE'
    elif key == b'/':      # Slash untuk search
        return 'SEARCH'
    elif key == b'f' or key == b'F':  # Filter
        return 'FILTER'
    elif key == b'q' or key == b'Q':  # Quit
        return 'QUIT'
    elif key == b'\x1b':   # ESC
        return 'ESC'
    
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

def draw_header(current_path, search_mode=False, search_query="", filter_ext=""):
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
    
    # Search/Filter info
    if search_mode:
        search_text = f" 🔍 Search: {search_query}_"
        padding = cols - len(search_text) - 2
        print("│" + search_text + " " * padding + "│")
    elif filter_ext:
        filter_text = f" 🔍 Filter: *.{filter_ext}"
        padding = cols - len(filter_text) - 2
        print("│" + filter_text + " " * padding + "│")
    
    # Separator
    print("├" + "─" * (cols - 2) + "┤")

def draw_footer(search_mode=False):
    """Gambar footer dengan help commands"""
    cols, _ = get_terminal_size()
    
    if search_mode:
        help_text = " [Type to search | Enter: Confirm | ESC: Cancel] "
    else:
        help_text = " [↑↓: Navigate | Enter: Open | /: Search | F: Filter | Backspace: Parent | Q: Quit] "
    
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

def search_items(items, query):
    """Filter items berdasarkan search query"""
    if not query:
        return items
    
    query_lower = query.lower()
    filtered = []
    
    # Keep ".." jika ada
    if items and items[0][0] == "..":
        filtered.append(items[0])
    
    # Filter items yang mengandung query
    for item in items:
        name = item[0]
        if name != ".." and query_lower in name.lower():
            filtered.append(item)
    
    return filtered

def filter_by_extension(items, extension):
    """Filter items berdasarkan extension"""
    if not extension:
        return items
    
    ext_lower = extension.lower()
    filtered = []
    
    # Keep ".." dan folders
    for item in items:
        name, is_dir, size, modified, full_path = item
        if name == ".." or is_dir:
            filtered.append(item)
        elif name.lower().endswith(f".{ext_lower}"):
            filtered.append(item)
    
    return filtered

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

def go_to_parent(current_path):
    """Naik ke parent directory"""
    parent_path = str(Path(current_path).parent)
    # Cek jika sudah di root
    if parent_path != current_path:
        return change_directory(parent_path)
    return None, []

# ============================================
# SEARCH MODE
# ============================================
def handle_search_input():
    """Handle input untuk search mode"""
    query = ""
    
    while True:
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter - confirm search
            return query, False
        elif key == b'\x1b':  # ESC - cancel search
            return "", True
        elif key == b'\x08':  # Backspace - hapus karakter
            if query:
                query = query[:-1]
        elif key == b'\xe0':  # Skip special keys (arrows)
            msvcrt.getch()  # Consume second byte
            continue
        else:
            # Tambah karakter (hanya alphanumeric dan beberapa simbol)
            try:
                char = key.decode('utf-8')
                if char.isprintable() and char not in ['\r', '\n']:
                    query += char
            except:
                continue
        
        # Return query untuk live update
        yield query

def handle_filter_input():
    """Handle input untuk filter extension"""
    extension = ""
    
    while True:
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter - confirm filter
            return extension, False
        elif key == b'\x1b':  # ESC - cancel filter
            return "", True
        elif key == b'\x08':  # Backspace - hapus karakter
            if extension:
                extension = extension[:-1]
        elif key == b'\xe0':  # Skip special keys
            msvcrt.getch()
            continue
        else:
            # Tambah karakter
            try:
                char = key.decode('utf-8')
                if char.isalnum() or char == '.':
                    extension += char
            except:
                continue
        
        yield extension

# ============================================
# UI RENDERING
# ============================================
def render_ui(current_path, items, selected_index, message="", search_mode=False, search_query="", filter_ext=""):
    """Render UI dengan data real"""
    clear_screen()
    
    cols, lines = get_terminal_size()
    
    # Header
    draw_header(current_path, search_mode, search_query, filter_ext)
    
    # Message (jika ada)
    if message:
        print(f" ⓘ {message}")
        print()
    
    # Calculate max displayable items (minus header/footer)
    extra_lines = 0
    if message:
        extra_lines += 2
    if search_mode or filter_ext:
        extra_lines += 1
    
    max_display = lines - 8 - extra_lines
    
    # File list
    if not items:
        print("   (No items found)")
    else:
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
    draw_footer(search_mode)

# ============================================
# MAIN PROGRAM
# ============================================
def main():
    # Start dari current directory
    current_path = os.getcwd()
    selected = 0
    message = ""
    filter_ext = ""
    
    # Scan directory pertama kali
    all_items = scan_directory(current_path)
    items = all_items
    
    # Render pertama
    render_ui(current_path, items, selected, message, filter_ext=filter_ext)
    
    while True:
        key = get_key()
        message = ""  # Reset message
        
        if key == 'UP':
            selected = max(0, selected - 1)
            render_ui(current_path, items, selected, message, filter_ext=filter_ext)
            
        elif key == 'DOWN':
            selected = min(len(items) - 1, selected + 1) if items else 0
            render_ui(current_path, items, selected, message, filter_ext=filter_ext)
            
        elif key == 'BACKSPACE':
            # Naik ke parent directory
            new_path, new_items = go_to_parent(current_path)
            if new_path:
                current_path = new_path
                all_items = new_items
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                selected = 0
                message = "Moved to parent directory"
            else:
                message = "Already at root directory"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext)
            
        elif key == 'ENTER':
            if items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                
                if is_dir:
                    # Masuk ke folder
                    new_path, new_items = change_directory(full_path)
                    if new_path:
                        current_path = new_path
                        all_items = new_items
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
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
                
                render_ui(current_path, items, selected, message, filter_ext=filter_ext)
        
        elif key == 'SEARCH':
            # Search mode
            search_query = ""
            for query in handle_search_input():
                search_query = query
                temp_items = search_items(all_items, search_query)
                render_ui(current_path, temp_items, 0, f"Searching: {len(temp_items)} results", 
                         search_mode=True, search_query=search_query, filter_ext=filter_ext)
            
            # After search confirmed or cancelled
            if search_query:
                items = search_items(all_items, search_query)
                selected = 0
                message = f"Search results: {len(items)} items found"
            else:
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext)
        
        elif key == 'FILTER':
            # Filter mode
            temp_ext = ""
            for ext in handle_filter_input():
                temp_ext = ext.lstrip('.')  # Remove leading dot if any
                temp_items = filter_by_extension(all_items, temp_ext)
                render_ui(current_path, temp_items, 0, f"Filter: *.{temp_ext} ({len(temp_items)} items)", 
                         search_mode=True, search_query=temp_ext, filter_ext=temp_ext)
            
            # After filter confirmed or cancelled
            filter_ext = temp_ext
            if filter_ext:
                items = filter_by_extension(all_items, filter_ext)
                selected = 0
                message = f"Filtered by *.{filter_ext}: {len(items)} items"
            else:
                items = all_items
                message = "Filter cleared"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext)
            
        elif key == 'ESC':
            # Clear search/filter
            filter_ext = ""
            items = all_items
            selected = 0
            message = "Filter cleared"
            render_ui(current_path, items, selected, message)
            
        elif key == 'QUIT':
            clear_screen()
            print("Goodbye!")
            break

if __name__ == "__main__":
>>>>>>> a719b70078d15924ecfd898400713743347eb98e
    main()