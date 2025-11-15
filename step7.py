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

def draw_header(current_path, search_mode=False, search_query="", filter_ext="", clipboard_info=""):
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
        help_text = " [C:Copy X:Cut V:Paste R:Rename D:Delete N:NewFolder /:Search F:Filter Q:Quit] "
    
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
def render_ui(current_path, items, selected_index, message="", search_mode=False, search_query="", filter_ext="", is_filter=False, clipboard_info=""):
    """Render UI dengan data real"""
    clear_screen()
    
    cols, lines = get_terminal_size()
    
    # Header
    draw_header(current_path, search_mode, search_query, filter_ext if not search_mode else (filter_ext if is_filter else None), clipboard_info)
    
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
    
    # Clipboard untuk copy/cut
    clipboard = None
    clipboard_mode = None  # 'copy' atau 'cut'
    
    # Scan directory pertama kali
    all_items = scan_directory(current_path)
    items = all_items
    
    # Render pertama
    render_ui(current_path, items, selected, message, filter_ext=filter_ext)
    
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
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info)
            
        elif key == 'DOWN':
            selected = min(len(items) - 1, selected + 1) if items else 0
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info)
            
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
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info)
            
        elif key == 'ENTER':
            if items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                
                if name == "..":
                    # Naik ke parent
                    new_path, new_items = change_directory(full_path)
                    if new_path:
                        current_path = new_path
                        all_items = new_items
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                        selected = 0
                        message = "Moved to parent directory"
                elif is_dir:
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
                
                render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info)
        
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
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info)
        
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
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info)
        
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
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
            else:
                message = "Clipboard is empty"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info)
        
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
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                    elif not cancelled:
                        message = "Rename cancelled"
                else:
                    message = "Cannot rename parent directory marker"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info)
        
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
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                        
                        # Adjust selected jika perlu
                        if selected >= len(items):
                            selected = max(0, len(items) - 1)
                    else:
                        message = "Delete cancelled"
                else:
                    message = "Cannot delete parent directory marker"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info)
        
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
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
            elif not cancelled:
                message = "Folder creation cancelled"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info)
        
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
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info)
        
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
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info)
            
        elif key == 'ESC':
            # Clear search/filter
            filter_ext = ""
            items = all_items
            selected = 0
            message = "Filter cleared"
            render_ui(current_path, items, selected, message, clipboard_info=clipboard_info)
            
        elif key == 'QUIT':
            clear_screen()
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()