"""
UI rendering functions
"""
import os
import shutil


def clear_screen():
    """Clear terminal screen (Windows)"""
    os.system('cls')


def get_terminal_size():
    """Get ukuran terminal (columns, lines)"""
    size = shutil.get_terminal_size()
    return size.columns, size.lines


def draw_header(current_path, search_mode=False, search_query="", filter_ext="", clipboard_info="", sort_mode="name", view_mode="detailed", selected_count=0):
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
    
    # Add selection count if any
    if selected_count > 0:
        info_text += f"  |  ✓ Selected: {selected_count}"
    
    padding = cols - len(info_text) - 2
    if padding > 0:
        print("│" + info_text + " " * padding + "│")
    else:
        # Text too long, truncate
        info_text = info_text[:cols-5] + "..."
        print("│" + info_text + "│")
    
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
        help_text = " [Space:Select Z:Compress E:Extract C:Copy X:Cut V:Paste D:Delete Q:Quit] "
    
    print("└" + "─" * (cols - 2) + "┘")
    print(help_text.center(cols))


def render_ui(current_path, items, selected_index, message="", search_mode=False, search_query="", filter_ext="", is_filter=False, clipboard_info="", sort_mode="name", view_mode="detailed", selected_items=None):
    """Render UI dengan data real"""
    from .sorting import format_item_display
    
    if selected_items is None:
        selected_items = set()
    
    clear_screen()
    
    cols, lines = get_terminal_size()
    
    # Header
    draw_header(current_path, search_mode, search_query, filter_ext if not search_mode else (filter_ext if is_filter else None), clipboard_info, sort_mode, view_mode, len(selected_items))
    
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
            
            # Check if item is selected
            is_selected = idx in selected_items
            
            if idx == selected_index:
                # Current cursor position
                if is_selected:
                    print(f" ✓> {display_text}")  # Selected + cursor
                else:
                    print(f" > {display_text}")   # Just cursor
            else:
                # Not at cursor
                if is_selected:
                    print(f" ✓  {display_text}")  # Just selected
                else:
                    print(f"   {display_text}")   # Normal
        
        # Info jika ada lebih banyak items
        if len(items) > max_display:
            print(f"\n   ... and {len(items) - max_display} more items")
    
    # Footer
    print()
    draw_footer(search_mode, is_filter)