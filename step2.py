import msvcrt
import os
import shutil

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

def render_ui(current_path, items, selected_index):
    """Render seluruh UI"""
    clear_screen()
    
    # Header
    draw_header(current_path)
    
    # File list
    for idx, item in enumerate(items):
        if idx == selected_index:
            # Item yang dipilih (dengan cursor)
            print(f" > {item}")
        else:
            # Item biasa
            print(f"   {item}")
    
    # Footer
    print()  # Empty line
    draw_footer()

# Test render UI
if __name__ == "__main__":
    # Data dummy untuk test
    test_path = "C:\\Users\\YourName\\Documents"
    test_items = [
        "📁 folder1/",
        "📁 folder2/",
        "📄 file1.txt",
        "📄 document.pdf",
        "📄 image.png"
    ]
    
    selected = 0
    
    # Render pertama kali
    render_ui(test_path, test_items, selected)
    
    # Test navigasi
    print("\nTekan arrow keys untuk test navigasi (Q untuk quit)")
    
    while True:
        key = get_key()
        
        if key == 'UP':
            selected = max(0, selected - 1)
            render_ui(test_path, test_items, selected)
        elif key == 'DOWN':
            selected = min(len(test_items) - 1, selected + 1)
            render_ui(test_path, test_items, selected)
        elif key == 'QUIT':
            clear_screen()
            print("Goodbye!")
            break