"""
Layout and column management
"""
import msvcrt
from .ui import clear_screen, draw_header, get_terminal_size


def show_layout_menu(current_path, current_columns, filter_ext, sort_mode):
    """Show column layout selection menu"""
    clear_screen()
    cols, _ = get_terminal_size()
    
    draw_header(current_path, filter_ext=filter_ext, sort_mode=sort_mode, num_columns=current_columns)
    
    print("\n 📐 Layout Options")
    print(" " + "─" * 40)
    
    options = [
        ("5", 1, "Single Column"),
        ("6", 2, "Two Columns"),
        ("7", 3, "Three Columns"),
        ("8", 4, "Four Columns"),
    ]
    
    for key, num, label in options:
        if current_columns == num:
            print(f" > [{key}] {label} ✓")
        else:
            print(f"   [{key}] {label}")
    
    print("\n " + "─" * 40)
    print(" [ESC] Cancel")
    
    while True:
        key = msvcrt.getch()
        
        if key == b'5':
            return 1, False
        elif key == b'6':
            return 2, False
        elif key == b'7':
            return 3, False
        elif key == b'8':
            return 4, False
        elif key == b'\x1b':  # ESC
            return current_columns, True