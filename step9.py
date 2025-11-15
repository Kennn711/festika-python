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
        elif key == b'S':  # Delete key
            return 'DELETE'
    elif key == b'\r':     # Enter
        return 'ENTER'
    elif key == b'\x08':   # Backspace
        return 'BACKSPACE'
    elif key == b'/':      # Slash untuk search
        return 'SEARCH'
    elif key == b'f' or key == b'F':  # Filter
        return 'FILTER'
    elif key == b'c' or key == b'C':  # Copy
        return 'COPY'
    elif key == b'x' or key == b'X':  # Cut (move)
        return 'CUT'
    elif key == b'v' or key == b'V':  # Paste
        return 'PASTE'
    elif key == b'r' or key == b'R':  # Rename
        return 'RENAME'
    elif key == b'd' or key == b'D':  # Delete
        return 'DELETE_KEY'
    elif key == b'n' or key == b'N':  # New folder
        return 'NEW_FOLDER'
    elif key == b't' or key == b'T':  # New file
        return 'NEW_FILE'
    elif key == b's' or key == b'S':  # Sort menu
        return 'SORT'
    elif key == b'w' or key == b'W':  # View mode
        return 'VIEW'
    elif key == b'q' or key == b'Q':  # Quit
        return 'QUIT'
    elif key == b'\x1b':   # ESC
        return 'ESC'
    elif key == b'1':      # Sort shortcuts
        return 'SORT_NAME'
    elif key == b'2':
        return 'SORT_SIZE'
    elif key == b'3':
        return 'SORT_DATE'
    elif key == b'4':
        return 'SORT_TYPE'
    
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

def draw_header(current_path, search_mode=False, search_query="", filter_ext="", clipboard_info="", sort_mode="name", view_mode="detailed"):
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
    
    # Sort & View info
    sort_icon = {"name": "📝", "size": "📊", "date": "📅", "type": "📂"}
    view_icon = {"detailed": "📋", "compact": "📄", "list": "📃"}
    
    info_text = f" {sort_icon.get(sort_mode, '📝')} Sort: {sort_mode.title()}  |  {view_icon.get(view_mode, '📋')} View: {view_mode.title()}"
    padding = cols - len(info_text) - 2
    print("│" + info_text + " " * padding + "│")
    
    # Clipboard info
    if clipboard_info:
        clip_text = f" 📋 {clipboard_info}"
        padding = cols - len(clip_text) - 2
        print("│" + clip_text + " " * padding + "│")
    
    # Search/Filter info
    if search_mode:
        if filter_ext is not None and search_query == filter_ext:
            # Filter mode
            filter_text = f" 🔍 Filter Extension: .{search_query}_"
        else:
            # Search mode
            filter_text = f" 🔍 Search: {search_query}_"
        padding = cols - len(filter_text) - 2
        print("│" + filter_text + " " * padding + "│")
    elif filter_ext:
        filter_text = f" 🔍 Active Filter: *.{filter_ext}"
        padding = cols - len(filter_text) - 2
        print("│" + filter_text + " " * padding + "│")
    
    # Separator
    print("├" + "─" * (cols - 2) + "┤")

def draw_footer(search_mode=False, is_filter_mode=False):
    """Gambar footer dengan help commands"""
    cols, _ = get_terminal_size()
    
    if search_mode:
        if is_filter_mode:
            help_text = " [Type extension | Enter: Apply | ESC: Cancel] "
        else:
            help_text = " [Type to search | Enter: Apply | ESC: Cancel] "
    else:
        help_text = " [S:Sort W:View C:Copy X:Cut V:Paste R:Rename D:Delete N:Folder T:File /:Search F:Filter Q:Quit] "
    
    print("└" + "─" * (cols - 2) + "┘")
    print(help_text.center(cols))

# ============================================
# SORTING FUNCTIONS
# ============================================
def sort_items(items, sort_mode="name", reverse=False):
    """
    Sort items berdasarkan mode yang dipilih
    Modes: name, size, date, type
    """
    # Pisahkan ".." dari items lain
    parent_item = None
    regular_items = []
    
    for item in items:
        if item[0] == "..":
            parent_item = item
        else:
            regular_items.append(item)
    
    # Sort berdasarkan mode
    if sort_mode == "name":
        # Sort by name (folders first, then files)
        regular_items.sort(key=lambda x: (not x[1], x[0].lower()), reverse=reverse)
    
    elif sort_mode == "size":
        # Sort by size (folders always first, then files by size)
        def get_size_value(item):
            if item[1]:  # folder
                return (-1, item[0].lower())  # Folders first, then alphabetically
            else:  # file
                size_str = item[2]
                if size_str == "N/A" or not size_str:
                    return (0, item[0].lower())
                
                # Parse size string to bytes for proper sorting
                try:
                    value, unit = size_str.split()
                    value = float(value)
                    multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
                    return (value * multipliers.get(unit, 1), item[0].lower())
                except:
                    return (0, item[0].lower())
        
        regular_items.sort(key=get_size_value, reverse=reverse)
    
    elif sort_mode == "date":
        # Sort by modification date
        def get_date_value(item):
            if item[1]:  # folder
                return (datetime.min if not reverse else datetime.max, item[0].lower())
            else:  # file
                try:
                    # Get actual file modification time
                    path = Path(item[4])
                    if path.exists():
                        mtime = path.stat().st_mtime
                        return (datetime.fromtimestamp(mtime), item[0].lower())
                except:
                    pass
                return (datetime.min if not reverse else datetime.max, item[0].lower())
        
        regular_items.sort(key=get_date_value, reverse=reverse)
    
    elif sort_mode == "type":
        # Sort by file extension/type
        def get_type_value(item):
            if item[1]:  # folder
                return ("", item[0].lower())
            else:
                # Get extension
                ext = Path(item[0]).suffix.lower()
                return (ext, item[0].lower())
        
        regular_items.sort(key=get_type_value, reverse=reverse)
    
    # Gabungkan kembali dengan ".." di depan
    result = []
    if parent_item:
        result.append(parent_item)
    result.extend(regular_items)
    
    return result

# ============================================
# VIEW MODES
# ============================================
def format_item_display_detailed(item, max_width):
    """Detailed view: icon + name + size + date"""
    name, is_dir, size, modified, _ = item
    
    icon = "📁" if is_dir else "📄"
    
    if is_dir:
        display = f"{icon} {name}/"
        padding = max_width - len(display) - 20
        if padding > 0:
            display += " " * padding + f"<DIR>".rjust(15)
    else:
        display = f"{icon} {name}"
        padding = max_width - len(display) - len(size) - 4
        if padding > 0:
            display += " " * padding + size
    
    return display

def format_item_display_compact(item, max_width):
    """Compact view: icon + name + size only"""
    name, is_dir, size, modified, _ = item
    
    icon = "📁" if is_dir else "📄"
    
    if is_dir:
        display = f"{icon} {name}/"
    else:
        display = f"{icon} {name}"
        if size and size != "N/A":
            padding = max_width - len(display) - len(size) - 4
            if padding > 0:
                display += " " * padding + size
    
    return display

def format_item_display_list(item, max_width):
    """List view: name only (no icons)"""
    name, is_dir, size, modified, _ = item
    
    if is_dir:
        return f"{name}/"
    else:
        return name

def format_item_display(item, max_width, view_mode="detailed"):
    """Format item berdasarkan view mode"""
    if view_mode == "detailed":
        return format_item_display_detailed(item, max_width)
    elif view_mode == "compact":
        return format_item_display_compact(item, max_width)
    elif view_mode == "list":
        return format_item_display_list(item, max_width)
    else:
        return format_item_display_detailed(item, max_width)

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
        
        # Default sort: folders first, then files (alphabetically)
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
    
    ext_lower = extension.lower().lstrip('.')
    filtered = []
    
    # Keep ".." dan folders
    for item in items:
        name, is_dir, size, modified, full_path = item
        if name == ".." or is_dir:
            filtered.append(item)
        elif name.lower().endswith(f".{ext_lower}"):
            filtered.append(item)
    
    return filtered

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
# FILE OPERATIONS
# ============================================
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

# ============================================
# SORT & VIEW MENUS
# ============================================
def show_sort_menu(current_path, current_sort, filter_ext):
    """Show sort options menu"""
    clear_screen()
    cols, _ = get_terminal_size()
    
    draw_header(current_path, filter_ext=filter_ext, sort_mode=current_sort)
    
    print("\n 📊 Sort Options")
    print(" " + "─" * 40)
    
    options = [
        ("1", "name", "Name (A-Z)", "📝"),
        ("2", "size", "Size (Smallest to Largest)", "📊"),
        ("3", "date", "Date Modified (Oldest to Newest)", "📅"),
        ("4", "type", "Type (Extension)", "📂"),
    ]
    
    for key, mode, label, icon in options:
        if current_sort == mode:
            print(f" > [{key}] {icon} {label} ✓")
        else:
            print(f"   [{key}] {icon} {label}")
    
    print("\n " + "─" * 40)
    print(" [R] Reverse current sort order")
    print(" [ESC] Cancel")
    
    while True:
        key = msvcrt.getch()
        
        if key == b'1':
            return "name", False, False
        elif key == b'2':
            return "size", False, False
        elif key == b'3':
            return "date", False, False
        elif key == b'4':
            return "type", False, False
        elif key == b'r' or key == b'R':
            return current_sort, True, False
        elif key == b'\x1b':  # ESC
            return current_sort, False, True

def show_view_menu(current_path, current_view, filter_ext, sort_mode):
    """Show view options menu"""
    clear_screen()
    cols, _ = get_terminal_size()
    
    draw_header(current_path, filter_ext=filter_ext, sort_mode=sort_mode, view_mode=current_view)
    
    print("\n 👁️  View Options")
    print(" " + "─" * 40)
    
    options = [
        ("1", "detailed", "Detailed (Icon + Name + Size + Info)", "📋"),
        ("2", "compact", "Compact (Icon + Name + Size)", "📄"),
        ("3", "list", "List (Name Only)", "📃"),
    ]
    
    for key, mode, label, icon in options:
        if current_view == mode:
            print(f" > [{key}] {icon} {label} ✓")
        else:
            print(f"   [{key}] {icon} {label}")
    
    print("\n " + "─" * 40)
    print(" [ESC] Cancel")
    
    while True:
        key = msvcrt.getch()
        
        if key == b'1':
            return "detailed", False
        elif key == b'2':
            return "compact", False
        elif key == b'3':
            return "list", False
        elif key == b'\x1b':  # ESC
            return current_view, True

# ============================================
# INPUT DIALOGS
# ============================================
def get_text_input(prompt, current_path, items, selected, filter_ext, initial_value=""):
    """Get text input dari user"""
    text = initial_value
    
    # Render dengan input prompt
    clear_screen()
    cols, _ = get_terminal_size()
    
    draw_header(current_path, filter_ext=filter_ext)
    print(f"\n {prompt}")
    print(f" > {text}_")
    print("\n [Enter: Confirm | ESC: Cancel]")
    
    while True:
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter
            return text, False
        elif key == b'\x1b':  # ESC
            return "", True
        elif key == b'\x08':  # Backspace
            if text:
                text = text[:-1]
        elif key == b'\xe0':  # Skip special keys
            msvcrt.getch()
            continue
        else:
            try:
                char = key.decode('utf-8')
                if char.isprintable():
                    text += char
            except:
                continue
        
        # Re-render
        clear_screen()
        draw_header(current_path, filter_ext=filter_ext)
        print(f"\n {prompt}")
        print(f" > {text}_")
        print("\n [Enter: Confirm | ESC: Cancel]")

def get_filename_input(current_path, filter_ext):
    """Get filename dengan extension dari user (2 step input)"""
    
    # Step 1: Input nama file
    clear_screen()
    draw_header(current_path, filter_ext=filter_ext)
    print(f"\n 📝 Create New File")
    print(f"\n Step 1: Enter filename (without extension)")
    print(f" > _")
    print("\n [Enter: Next | ESC: Cancel]")
    
    filename = ""
    while True:
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter - lanjut ke step 2
            if filename:
                break
            else:
                continue
        elif key == b'\x1b':  # ESC
            return "", True
        elif key == b'\x08':  # Backspace
            if filename:
                filename = filename[:-1]
        elif key == b'\xe0':  # Skip special keys
            msvcrt.getch()
            continue
        else:
            try:
                char = key.decode('utf-8')
                # Hanya izinkan karakter valid untuk nama file
                if char.isprintable() and char not in ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '.']:
                    filename += char
            except:
                continue
        
        # Re-render
        clear_screen()
        draw_header(current_path, filter_ext=filter_ext)
        print(f"\n 📝 Create New File")
        print(f"\n Step 1: Enter filename (without extension)")
        print(f" > {filename}_")
        print("\n [Enter: Next | ESC: Cancel]")
    
    # Step 2: Input extension
    clear_screen()
    draw_header(current_path, filter_ext=filter_ext)
    print(f"\n 📝 Create New File")
    print(f"\n Filename: {filename}")
    print(f"\n Step 2: Enter file extension (e.g., txt, py, json)")
    print(f" > ._")
    print("\n [Enter: Create | ESC: Cancel]")
    print("\n Common extensions: txt, py, json, md, html, css, js, xml, csv")
    
    extension = ""
    while True:
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter - create file
            # Jika tidak ada extension, default ke .txt
            if not extension:
                extension = "txt"
            break
        elif key == b'\x1b':  # ESC
            return "", True
        elif key == b'\x08':  # Backspace
            if extension:
                extension = extension[:-1]
        elif key == b'\xe0':  # Skip special keys
            msvcrt.getch()
            continue
        else:
            try:
                char = key.decode('utf-8')
                # Hanya izinkan alphanumeric untuk extension
                if char.isalnum():
                    extension += char
            except:
                continue
        
        # Re-render
        clear_screen()
        draw_header(current_path, filter_ext=filter_ext)
        print(f"\n 📝 Create New File")
        print(f"\n Filename: {filename}")
        print(f"\n Step 2: Enter file extension (e.g., txt, py, json)")
        print(f" > .{extension}_")
        print("\n [Enter: Create | ESC: Cancel]")
        print("\n Common extensions: txt, py, json, md, html, css, js, xml, csv")
    
    # Gabungkan filename dan extension
    full_filename = f"{filename}.{extension}"
    return full_filename, False

def confirm_dialog(message, current_path, filter_ext):
    """Confirmation dialog (Y/N)"""
    clear_screen()
    cols, _ = get_terminal_size()
    
    draw_header(current_path, filter_ext=filter_ext)
    print(f"\n ⚠️  {message}")
    print("\n [Y: Yes | N: No]")
    
    while True:
        key = msvcrt.getch()
        
        if key == b'y' or key == b'Y':
            return True
        elif key == b'n' or key == b'N' or key == b'\x1b':
            return False

# ============================================
# SEARCH MODE
# ============================================
def search_mode_input(current_path, all_items, filter_ext):
    """Handle search mode dengan live update"""
    query = ""
    
    # Render awal dengan input box kosong
    temp_items = all_items
    render_ui(current_path, temp_items, 0, f"Search results: {len(temp_items)} items", 
             search_mode=True, search_query=query, filter_ext=None)
    
    while True:
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter - confirm search
            return query, False
        elif key == b'\x1b':  # ESC - cancel search
            return "", True
        elif key == b'\x08':  # Backspace - hapus karakter
            if query:
                query = query[:-1]
                temp_items = search_items(all_items, query)
                render_ui(current_path, temp_items, 0, f"Search results: {len(temp_items)} items", 
                         search_mode=True, search_query=query, filter_ext=None)
        elif key == b'\xe0':  # Skip special keys (arrows)
            msvcrt.getch()  # Consume second byte
            continue
        else:
            # Tambah karakter (hanya alphanumeric dan beberapa simbol)
            try:
                char = key.decode('utf-8')
                if char.isprintable() and char not in ['\r', '\n']:
                    query += char
                    # Live update hasil search
                    temp_items = search_items(all_items, query)
                    render_ui(current_path, temp_items, 0, f"Search results: {len(temp_items)} items", 
                             search_mode=True, search_query=query, filter_ext=None)
            except:
                continue

def filter_mode_input(current_path, all_items, current_filter):
    """Handle filter mode dengan live update"""
    extension = current_filter if current_filter else ""
    
    # Render awal dengan input box
    temp_items = filter_by_extension(all_items, extension) if extension else all_items
    render_ui(current_path, temp_items, 0, f"Filter: *.{extension} ({len(temp_items)} items)", 
             search_mode=True, search_query=extension, filter_ext=extension, is_filter=True)
    
    while True:
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter - confirm filter
            return extension, False
        elif key == b'\x1b':  # ESC - cancel filter
            return current_filter, True
        elif key == b'\x08':  # Backspace - hapus karakter
            if extension:
                extension = extension[:-1]
                temp_items = filter_by_extension(all_items, extension) if extension else all_items
                render_ui(current_path, temp_items, 0, f"Filter: *.{extension} ({len(temp_items)} items)", 
                         search_mode=True, search_query=extension, filter_ext=extension, is_filter=True)
        elif key == b'\xe0':  # Skip special keys
            msvcrt.getch()
            continue
        else:
            # Tambah karakter
            try:
                char = key.decode('utf-8')
                if char.isalnum() or char == '.':
                    extension += char
                    extension = extension.lstrip('.')  # Remove leading dots
                    # Live update hasil filter
                    temp_items = filter_by_extension(all_items, extension) if extension else all_items
                    render_ui(current_path, temp_items, 0, f"Filter: *.{extension} ({len(temp_items)} items)", 
                             search_mode=True, search_query=extension, filter_ext=extension, is_filter=True)
            except:
                continue

# ============================================
# UI RENDERING
# ============================================
def render_ui(current_path, items, selected_index, message="", search_mode=False, search_query="", filter_ext="", is_filter=False, clipboard_info="", sort_mode="name", view_mode="detailed"):
    """Render UI dengan data real"""
    clear_screen()
    
    cols, lines = get_terminal_size()
    
    # Header
    draw_header(current_path, search_mode, search_query, filter_ext if not search_mode else (filter_ext if is_filter else None), clipboard_info, sort_mode, view_mode)
    
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
    if clipboard_info:
        extra_lines += 1
    # Sort & View info line
    extra_lines += 1
    
    max_display = lines - 8 - extra_lines
    
    # File list
    if not items:
        print("   (No items found)")
    else:
        for idx, item in enumerate(items[:max_display]):
            display_text = format_item_display(item, cols - 6, view_mode)
            
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
    draw_footer(search_mode, is_filter)

# ============================================
# MAIN PROGRAM
# ============================================
def main():
    # Start dari current directory
    current_path = os.getcwd()
    selected = 0
    message = ""
    filter_ext = ""
    
    # Sort & View settings
    sort_mode = "name"  # name, size, date, type
    sort_reverse = False
    view_mode = "detailed"  # detailed, compact, list
    
    # Clipboard untuk copy/cut
    clipboard = None
    clipboard_mode = None  # 'copy' atau 'cut'
    
    # Scan directory pertama kali
    all_items = scan_directory(current_path)
    items = sort_items(all_items, sort_mode, sort_reverse)
    
    # Render pertama
    render_ui(current_path, items, selected, message, filter_ext=filter_ext, sort_mode=sort_mode, view_mode=view_mode)
    
    while True:
        # Generate clipboard info text
        clipboard_info = ""
        if clipboard:
            mode_text = "Copy" if clipboard_mode == 'copy' else "Cut"
            clipboard_info = f"{mode_text}: {Path(clipboard).name}"
        
        key = get_key()
        message = ""  # Reset message
        
        if key == 'UP':
            selected = max(0, selected - 1)
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
            
        elif key == 'DOWN':
            selected = min(len(items) - 1, selected + 1) if items else 0
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
            
        elif key == 'BACKSPACE':
            # Naik ke parent directory
            new_path, new_items = go_to_parent(current_path)
            if new_path:
                current_path = new_path
                all_items = new_items
                all_items = sort_items(all_items, sort_mode, sort_reverse)
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                selected = 0
                message = "Moved to parent directory"
            else:
                message = "Already at root directory"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
            
        elif key == 'ENTER':
            if items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                
                if name == "..":
                    # Naik ke parent
                    new_path, new_items = change_directory(full_path)
                    if new_path:
                        current_path = new_path
                        all_items = new_items
                        all_items = sort_items(all_items, sort_mode, sort_reverse)
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                        selected = 0
                        message = "Moved to parent directory"
                elif is_dir:
                    # Masuk ke folder
                    new_path, new_items = change_directory(full_path)
                    if new_path:
                        current_path = new_path
                        all_items = new_items
                        all_items = sort_items(all_items, sort_mode, sort_reverse)
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
                
                render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
        
        elif key == 'SORT':
            # Show sort menu
            new_sort, reverse, cancelled = show_sort_menu(current_path, sort_mode, filter_ext)
            
            if not cancelled:
                if reverse:
                    sort_reverse = not sort_reverse
                    message = f"Sort order reversed: {'Descending' if sort_reverse else 'Ascending'}"
                else:
                    sort_mode = new_sort
                    message = f"Sorted by: {sort_mode.title()}"
                
                # Re-sort items
                all_items = sort_items(all_items, sort_mode, sort_reverse)
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                selected = 0
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
        
        elif key in ['SORT_NAME', 'SORT_SIZE', 'SORT_DATE', 'SORT_TYPE']:
            # Quick sort shortcuts
            sort_map = {
                'SORT_NAME': 'name',
                'SORT_SIZE': 'size',
                'SORT_DATE': 'date',
                'SORT_TYPE': 'type'
            }
            sort_mode = sort_map[key]
            sort_reverse = False
            message = f"Sorted by: {sort_mode.title()}"
            
            # Re-sort items
            all_items = sort_items(all_items, sort_mode, sort_reverse)
            items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
            selected = 0
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
        
        elif key == 'VIEW':
            # Show view menu
            new_view, cancelled = show_view_menu(current_path, view_mode, filter_ext, sort_mode)
            
            if not cancelled:
                view_mode = new_view
                message = f"View mode: {view_mode.title()}"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
        
        elif key == 'COPY':
            # Copy item ke clipboard
            if items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                if name != "..":
                    clipboard = full_path
                    clipboard_mode = 'copy'
                    message = f"Copied to clipboard: {name}"
                else:
                    message = "Cannot copy parent directory marker"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
        
        elif key == 'CUT':
            # Cut item ke clipboard
            if items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                if name != "..":
                    clipboard = full_path
                    clipboard_mode = 'cut'
                    message = f"Cut to clipboard: {name}"
                else:
                    message = "Cannot cut parent directory marker"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
        
        elif key == 'PASTE':
            # Paste dari clipboard
            if clipboard:
                if clipboard_mode == 'copy':
                    success, msg = copy_item(clipboard, current_path)
                else:  # cut
                    success, msg = move_item(clipboard, current_path)
                    if success:
                        clipboard = None
                        clipboard_mode = None
                
                message = msg
                
                # Refresh directory
                all_items = scan_directory(current_path)
                all_items = sort_items(all_items, sort_mode, sort_reverse)
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
            else:
                message = "Clipboard is empty"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
        
        elif key == 'RENAME':
            # Rename item
            if items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                
                if name != "..":
                    new_name, cancelled = get_text_input(
                        f"Rename '{name}' to:", 
                        current_path, items, selected, filter_ext, 
                        initial_value=name
                    )
                    
                    if not cancelled and new_name and new_name != name:
                        success, msg = rename_item(full_path, new_name)
                        message = msg
                        
                        # Refresh directory
                        all_items = scan_directory(current_path)
                        all_items = sort_items(all_items, sort_mode, sort_reverse)
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                    elif not cancelled:
                        message = "Rename cancelled"
                else:
                    message = "Cannot rename parent directory marker"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
        
        elif key == 'DELETE_KEY' or key == 'DELETE':
            # Delete item
            if items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                
                if name != "..":
                    # Confirmation
                    item_type = "folder" if is_dir else "file"
                    confirmed = confirm_dialog(
                        f"Delete {item_type} '{name}'? This cannot be undone!",
                        current_path, filter_ext
                    )
                    
                    if confirmed:
                        success, msg = delete_item(full_path)
                        message = msg
                        
                        # Refresh directory
                        all_items = scan_directory(current_path)
                        all_items = sort_items(all_items, sort_mode, sort_reverse)
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                        
                        # Adjust selected jika perlu
                        if selected >= len(items):
                            selected = max(0, len(items) - 1)
                    else:
                        message = "Delete cancelled"
                else:
                    message = "Cannot delete parent directory marker"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
        
        elif key == 'NEW_FOLDER':
            # Create new folder
            folder_name, cancelled = get_text_input(
                "New folder name:",
                current_path, items, selected, filter_ext
            )
            
            if not cancelled and folder_name:
                success, msg = create_folder(current_path, folder_name)
                message = msg
                
                # Refresh directory
                all_items = scan_directory(current_path)
                all_items = sort_items(all_items, sort_mode, sort_reverse)
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
            elif not cancelled:
                message = "Folder creation cancelled"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
        
        elif key == 'NEW_FILE':
            # Create new file dengan extension
            filename, cancelled = get_filename_input(current_path, filter_ext)
            
            if not cancelled and filename:
                success, msg = create_file(current_path, filename)
                message = msg
                
                # Refresh directory
                all_items = scan_directory(current_path)
                all_items = sort_items(all_items, sort_mode, sort_reverse)
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
            elif not cancelled:
                message = "File creation cancelled"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
        
        elif key == 'SEARCH':
            # Langsung masuk search mode dengan input box
            search_query, cancelled = search_mode_input(current_path, all_items, filter_ext)
            
            if not cancelled and search_query:
                items = search_items(all_items, search_query)
                selected = 0
                message = f"Search results: {len(items)} items found for '{search_query}'"
                filter_ext = ""  # Clear filter saat search
            else:
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                message = "Search cancelled"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
        
        elif key == 'FILTER':
            # Langsung masuk filter mode dengan input box
            new_filter, cancelled = filter_mode_input(current_path, all_items, filter_ext)
            
            if not cancelled:
                filter_ext = new_filter
                if filter_ext:
                    items = filter_by_extension(all_items, filter_ext)
                    selected = 0
                    message = f"Filtered by *.{filter_ext}: {len(items)} items"
                else:
                    items = all_items
                    selected = 0
                    message = "Filter cleared"
            else:
                message = "Filter cancelled"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
            
        elif key == 'ESC':
            # Clear search/filter
            filter_ext = ""
            items = all_items
            selected = 0
            message = "Filter cleared"
            render_ui(current_path, items, selected, message, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode)
            
        elif key == 'QUIT':
            clear_screen()
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()