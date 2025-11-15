import msvcrt
import os
import shutil
from pathlib import Path
from datetime import datetime

# ... (fungsi-fungsi sebelumnya tetap ada) ...

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
        print(f"Permission denied: {path}")
    except Exception as e:
        print(f"Error scanning directory: {e}")
    
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

# Update render_ui untuk terima data real
def render_ui_v2(current_path, items, selected_index):
    """Render UI dengan data real"""
    clear_screen()
    
    cols, lines = get_terminal_size()
    
    # Header
    draw_header(current_path)
    
    # Calculate max displayable items (minus header/footer)
    max_display = lines - 8
    
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

# Main program untuk test
if __name__ == "__main__":
    # Start dari current directory
    current_path = os.getcwd()
    selected = 0
    
    # Scan directory pertama kali
    items = scan_directory(current_path)
    
    # Render pertama
    render_ui_v2(current_path, items, selected)
    
    print("\nNavigasi:")
    print("↑↓: Pindah cursor")
    print("Q: Keluar")
    print("\n(Enter untuk open folder - next step)")
    
    while True:
        key = get_key()
        
        if key == 'UP':
            selected = max(0, selected - 1)
            render_ui_v2(current_path, items, selected)
            
        elif key == 'DOWN':
            selected = min(len(items) - 1, selected + 1)
            render_ui_v2(current_path, items, selected)
            
        elif key == 'QUIT':
            clear_screen()
            print("Goodbye!")
            break