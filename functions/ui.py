"""
UI rendering functions
"""
import os
import shutil
import math


def clear_screen():
    """Clear terminal screen (Windows)"""
    os.system('cls')


def get_terminal_size():
    """Get ukuran terminal (columns, lines)"""
    size = shutil.get_terminal_size()
    return size.columns, size.lines


def draw_header(current_path, search_mode=False, search_query="", filter_ext="", clipboard_info="", sort_mode="name", view_mode="detailed", selected_count=0, num_columns=1, page_info=""):
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
    
    info_text = f" {sort_icon.get(sort_mode, '📝')} Sort: {sort_mode.title()}  |  {view_icon.get(view_mode, '📋')} View: {view_mode.title()}  |  Columns: {num_columns}"
    
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
    
    # Page info
    if page_info:
        padding = cols - len(page_info) - 2
        print("│" + page_info + " " * padding + "│")
    
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


def draw_footer(search_mode=False, is_filter_mode=False, has_pagination=False):
    """Gambar footer dengan help commands"""
    cols, _ = get_terminal_size()
    
    if search_mode:
        if is_filter_mode:
            help_text = " [Type extension | Enter: Apply | ESC: Cancel] "
        else:
            help_text = " [Type to search | Enter: Apply | ESC: Cancel] "
    else:
        if has_pagination:
            help_text = " [PgUp/PgDn:Page ←→:Navigate L:Layout Space:Select Z:Compress E:Extract Q:Quit] "
        else:
            help_text = " [L:Layout Space:Select Z:Compress E:Extract C:Copy X:Cut V:Paste D:Delete Q:Quit] "
    
    print("└" + "─" * (cols - 2) + "┘")
    print(help_text.center(cols))


def render_ui_single_column(current_path, items, selected_index, message="", search_mode=False, search_query="", filter_ext="", is_filter=False, clipboard_info="", sort_mode="name", view_mode="detailed", selected_items=None, page=0, items_per_page=20):
    """Render UI single column dengan pagination"""
    from .sorting import format_item_display
    
    if selected_items is None:
        selected_items = set()
    
    clear_screen()
    
    cols, lines = get_terminal_size()
    
    # Calculate pagination
    total_pages = math.ceil(len(items) / items_per_page) if items else 1
    current_page = page + 1
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(items))
    visible_items = items[start_idx:end_idx] if items else []
    
    # Page info
    page_info = ""
    if len(items) > items_per_page:
        page_info = f" Page {current_page}/{total_pages} ({len(items)} items total)"
    
    # Header
    draw_header(current_path, search_mode, search_query, filter_ext if not search_mode else (filter_ext if is_filter else None), clipboard_info, sort_mode, view_mode, len(selected_items), 1, page_info)
    
    # Message (jika ada)
    if message:
        print(f" ⓘ {message}")
        print()
    
    # File list
    if not visible_items:
        print("   (No items found)")
    else:
        for idx, item in enumerate(visible_items):
            actual_idx = start_idx + idx
            display_text = format_item_display(item, cols - 6, view_mode)
            
            # Check if item is selected
            is_selected = actual_idx in selected_items
            
            if actual_idx == selected_index:
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
    
    # Footer
    print()
    draw_footer(search_mode, is_filter, len(items) > items_per_page)


def render_ui_multi_column(current_path, items, selected_index, message="", search_mode=False, search_query="", filter_ext="", is_filter=False, clipboard_info="", sort_mode="name", view_mode="detailed", selected_items=None, num_columns=2, page=0):
    """Render UI multi-column dengan pagination"""
    from .sorting import format_item_display
    
    if selected_items is None:
        selected_items = set()
    
    clear_screen()
    
    cols, lines = get_terminal_size()
    
    # Calculate items per page based on screen height
    extra_lines = 8  # Header + footer + margins
    if message:
        extra_lines += 2
    if search_mode or filter_ext:
        extra_lines += 1
    if clipboard_info:
        extra_lines += 1
    if len(items) > (lines - extra_lines):
        extra_lines += 1  # Page info
    
    rows_per_page = lines - extra_lines
    items_per_page = rows_per_page * num_columns
    
    # Calculate pagination
    total_pages = math.ceil(len(items) / items_per_page) if items else 1
    current_page = page + 1
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(items))
    visible_items = items[start_idx:end_idx] if items else []
    
    # Page info
    page_info = ""
    if len(items) > items_per_page:
        page_info = f" Page {current_page}/{total_pages} ({len(items)} items total)"
    
    # Header
    draw_header(current_path, search_mode, search_query, filter_ext if not search_mode else (filter_ext if is_filter else None), clipboard_info, sort_mode, view_mode, len(selected_items), num_columns, page_info)
    
    # Message (jika ada)
    if message:
        print(f" ⓘ {message}")
        print()
    
    # Calculate column width
    column_width = (cols - 4) // num_columns
    
    # File list in columns
    if not visible_items:
        print("   (No items found)")
    else:
        # Split items into rows
        num_rows = math.ceil(len(visible_items) / num_columns)
        
        for row in range(num_rows):
            line = " "
            
            for col in range(num_columns):
                idx = row + (col * num_rows)
                
                if idx < len(visible_items):
                    actual_idx = start_idx + idx
                    item = visible_items[idx]
                    
                    # Format display dengan column width
                    display_text = format_item_display(item, column_width - 5, view_mode)
                    
                    # Truncate jika terlalu panjang
                    if len(display_text) > column_width - 5:
                        display_text = display_text[:column_width-8] + "..."
                    
                    # Check if item is selected
                    is_selected = actual_idx in selected_items
                    
                    # Add selection/cursor indicators
                    if actual_idx == selected_index:
                        if is_selected:
                            prefix = "✓>"
                        else:
                            prefix = "> "
                    else:
                        if is_selected:
                            prefix = "✓ "
                        else:
                            prefix = "  "
                    
                    # Add to line with padding
                    cell = prefix + display_text
                    cell = cell[:column_width-1].ljust(column_width-1)
                    line += cell + " "
                else:
                    # Empty cell
                    line += " " * column_width
            
            print(line)
    
    # Footer
    print()
    draw_footer(search_mode, is_filter, len(items) > items_per_page)


def render_ui(current_path, items, selected_index, message="", search_mode=False, search_query="", filter_ext="", is_filter=False, clipboard_info="", sort_mode="name", view_mode="detailed", selected_items=None, num_columns=1, page=0):
    """Render UI dengan single atau multi-column"""
    if num_columns == 1:
        render_ui_single_column(current_path, items, selected_index, message, search_mode, search_query, filter_ext, is_filter, clipboard_info, sort_mode, view_mode, selected_items, page)
    else:
        render_ui_multi_column(current_path, items, selected_index, message, search_mode, search_query, filter_ext, is_filter, clipboard_info, sort_mode, view_mode, selected_items, num_columns, page)