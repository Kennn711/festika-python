"""
Sorting and view mode functions
"""
import msvcrt
from pathlib import Path
from datetime import datetime
from .ui import clear_screen, draw_header, get_terminal_size


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