"""
File Explorer - Main Application
Terminal-based File Explorer for Windows
"""
import os
import math
from pathlib import Path

# Import semua functions dari package
from functions import (
    # Keyboard
    get_key,
    
    # UI
    clear_screen,
    render_ui,
    get_terminal_size,
    
    # File System
    scan_directory,
    open_file,
    change_directory,
    go_to_parent,
    
    # File Operations
    copy_item,
    move_item,
    delete_item,
    rename_item,
    create_folder,
    create_file,
    copy_multiple_items,
    move_multiple_items,
    delete_multiple_items,
    
    # Sorting
    sort_items,
    show_sort_menu,
    show_view_menu,
    
    # Search & Filter
    filter_by_extension,
    search_mode_input,
    filter_mode_input,
    
    # Dialogs
    get_text_input,
    get_filename_input,
    confirm_dialog,
    
    # Compression
    is_archive,
    compress_to_zip,
    compress_to_7z,
    compress_to_rar,
    extract_archive,
    show_compression_menu,
    
    # Layout
    show_layout_menu,
)


def calculate_layout_info(num_columns, total_items):
    """Calculate layout information and adjust columns if needed"""
    cols, lines = get_terminal_size()
    
    # Calculate available space
    extra_lines = 8  # Base overhead (header + footer)
    available_rows = lines - extra_lines
    
    # Determine effective columns based on items
    effective_columns = num_columns
    
    if num_columns > 1:
        # Calculate minimum items needed for multi-column layout
        min_items_for_columns = available_rows * num_columns
        
        # If not enough items to fill all columns, reduce column count
        if total_items < min_items_for_columns:
            # Try to find optimal column count
            for cols_test in range(num_columns, 0, -1):
                if total_items >= available_rows * cols_test or cols_test == 1:
                    effective_columns = cols_test
                    break
    
    # Calculate items per page with effective columns
    rows_per_page = available_rows
    items_per_page = rows_per_page * effective_columns
    
    return effective_columns, items_per_page, rows_per_page


def get_position_in_grid(selected, num_columns, rows_per_page):
    """Get row and column position of selected item in grid"""
    if num_columns == 1:
        return selected, 0
    
    # In multi-column layout, items are arranged in column-major order
    row = selected % rows_per_page
    col = selected // rows_per_page
    
    return row, col


def move_in_grid(selected, direction, num_columns, rows_per_page, total_items):
    """Calculate new selection based on direction in grid layout"""
    if total_items == 0:
        return 0
    
    if num_columns == 1:
        # Single column - simple up/down
        if direction == 'UP':
            return max(0, selected - 1)
        elif direction == 'DOWN':
            return min(total_items - 1, selected + 1)
        return selected
    
    # Multi-column layout
    current_row, current_col = get_position_in_grid(selected, num_columns, rows_per_page)
    
    if direction == 'UP':
        # Move up one row
        new_row = current_row - 1
        if new_row < 0:
            # Wrap to bottom of previous column
            new_col = current_col - 1
            if new_col < 0:
                return 0  # Already at top-left
            new_row = rows_per_page - 1
            new_selected = new_col * rows_per_page + new_row
            return min(total_items - 1, max(0, new_selected))
        else:
            new_selected = current_col * rows_per_page + new_row
            return min(total_items - 1, new_selected)
    
    elif direction == 'DOWN':
        # Move down one row
        new_row = current_row + 1
        new_selected = current_col * rows_per_page + new_row
        
        if new_selected >= total_items:
            # Try to wrap to top of next column
            new_col = current_col + 1
            if new_col >= num_columns:
                return total_items - 1  # Already at bottom-right
            new_selected = new_col * rows_per_page
            return min(total_items - 1, new_selected)
        
        return new_selected
    
    elif direction == 'LEFT':
        # Move to previous column
        new_col = current_col - 1
        if new_col < 0:
            return selected  # Already at leftmost column
        
        new_selected = new_col * rows_per_page + current_row
        return min(total_items - 1, max(0, new_selected))
    
    elif direction == 'RIGHT':
        # Move to next column
        new_col = current_col + 1
        if new_col >= num_columns:
            return selected  # Already at rightmost column
        
        new_selected = new_col * rows_per_page + current_row
        
        if new_selected >= total_items:
            # Target position doesn't exist, stay in current position
            return selected
        
        return new_selected
    
    return selected


def main():
    """Main application loop"""
    # Start dari current directory
    current_path = os.getcwd()
    selected = 0
    message = ""
    filter_ext = ""
    
    # Sort & View settings
    sort_mode = "name"  # name, size, date, type
    sort_reverse = False
    view_mode = "detailed"  # detailed, compact, list
    
    # Layout settings
    num_columns = 1  # Number of columns (1-4) - user preference
    current_page = 0  # Current page for pagination
    
    # Multi-selection
    selected_items = set()  # Set of indices yang di-select
    
    # Clipboard untuk copy/cut
    clipboard = None
    clipboard_mode = None  # 'copy' atau 'cut'
    clipboard_items = []  # List of paths untuk multi-item clipboard
    
    # Scan directory pertama kali
    all_items = scan_directory(current_path)
    items = sort_items(all_items, sort_mode, sort_reverse)
    
    # Render pertama
    effective_columns, items_per_page, rows_per_page = calculate_layout_info(num_columns, len(items))
    render_ui(current_path, items, selected, message, filter_ext=filter_ext, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
    
    while True:
        # Generate clipboard info text
        clipboard_info = ""
        if clipboard_items:
            mode_text = "Copy" if clipboard_mode == 'copy' else "Cut"
            count = len(clipboard_items)
            if count == 1:
                clipboard_info = f"{mode_text}: {Path(clipboard_items[0]).name}"
            else:
                clipboard_info = f"{mode_text}: {count} items"
        
        key = get_key()
        message = ""  # Reset message
        
        # Calculate effective layout
        effective_columns, items_per_page, rows_per_page = calculate_layout_info(num_columns, len(items))
        total_pages = math.ceil(len(items) / items_per_page) if items else 1
        
        # Ensure current page is valid
        current_page = max(0, min(current_page, total_pages - 1))
        
        # Calculate visible range for current page
        start_idx = current_page * items_per_page
        end_idx = min(start_idx + items_per_page, len(items))
        
        if key == 'UP':
            new_selected = move_in_grid(selected, 'UP', effective_columns, rows_per_page, len(items))
            selected = new_selected
            
            # Adjust page if selected item is before current page
            if selected < start_idx:
                current_page = max(0, current_page - 1)
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
            
        elif key == 'DOWN':
            new_selected = move_in_grid(selected, 'DOWN', effective_columns, rows_per_page, len(items))
            selected = new_selected
            
            # Adjust page if selected item is after current page
            if selected >= end_idx:
                current_page = min(total_pages - 1, current_page + 1)
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'LEFT':
            if effective_columns > 1:
                new_selected = move_in_grid(selected, 'LEFT', effective_columns, rows_per_page, len(items))
                selected = new_selected
                
                # Adjust page if needed
                if selected < start_idx:
                    current_page = max(0, current_page - 1)
                
                render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'RIGHT':
            if effective_columns > 1:
                new_selected = move_in_grid(selected, 'RIGHT', effective_columns, rows_per_page, len(items))
                selected = new_selected
                
                # Adjust page if needed
                if selected >= end_idx:
                    current_page = min(total_pages - 1, current_page + 1)
                
                render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'PAGE_UP':
            # Go to previous page
            if current_page > 0:
                current_page -= 1
                # Move selection to first item of new page
                selected = current_page * items_per_page
                message = f"Page {current_page + 1}/{total_pages}"
            else:
                message = "Already at first page"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'PAGE_DOWN':
            # Go to next page
            if current_page < total_pages - 1:
                current_page += 1
                # Move selection to first item of new page
                selected = current_page * items_per_page
                message = f"Page {current_page + 1}/{total_pages}"
            else:
                message = "Already at last page"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'SPACE':
            # Toggle selection untuk item saat ini
            if items and selected < len(items):
                name = items[selected][0]
                if name != "..":  # Don't select parent marker
                    if selected in selected_items:
                        selected_items.remove(selected)
                        message = f"Deselected: {name}"
                    else:
                        selected_items.add(selected)
                        message = f"Selected: {name}"
                else:
                    message = "Cannot select parent directory marker"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'SELECT_ALL':
            # Select/Deselect all items (excluding "..")
            if selected_items:
                # If something is selected, deselect all
                selected_items.clear()
                message = "Deselected all items"
            else:
                # Select all (except "..")
                for idx, item in enumerate(items):
                    if item[0] != "..":
                        selected_items.add(idx)
                message = f"Selected {len(selected_items)} items"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'LAYOUT':
            # Show layout menu
            new_columns, cancelled = show_layout_menu(current_path, num_columns, filter_ext, sort_mode)
            
            if not cancelled:
                num_columns = new_columns
                current_page = 0  # Reset to first page when changing layout
                selected = 0
                
                # Calculate effective columns with new preference
                effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
                
                if effective_columns < num_columns:
                    message = f"Layout: {effective_columns} column{'s' if effective_columns > 1 else ''} (auto-adjusted from {num_columns})"
                else:
                    message = f"Layout: {num_columns} column{'s' if num_columns > 1 else ''}"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key in ['COL_1', 'COL_2', 'COL_3', 'COL_4']:
            # Quick column shortcuts
            column_map = {
                'COL_1': 1,
                'COL_2': 2,
                'COL_3': 3,
                'COL_4': 4
            }
            num_columns = column_map[key]
            current_page = 0
            selected = 0
            
            # Calculate effective columns
            effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
            
            if effective_columns < num_columns:
                message = f"Layout: {effective_columns} column{'s' if effective_columns > 1 else ''} (auto-adjusted)"
            else:
                message = f"Layout: {num_columns} column{'s' if num_columns > 1 else ''}"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'COMPRESS':
            # Compress selected items or current item
            items_to_compress = []
            
            if selected_items:
                # Multi-select mode
                for idx in selected_items:
                    if idx < len(items) and items[idx][0] != "..":
                        items_to_compress.append(items[idx][4])  # full_path
            elif items and selected < len(items):
                # Single item mode
                name, is_dir, size, modified, full_path = items[selected]
                if name != "..":
                    items_to_compress.append(full_path)
            
            if items_to_compress:
                # Show compression menu
                format_type, cancelled = show_compression_menu(current_path, filter_ext)
                
                if not cancelled:
                    # Get archive name
                    if len(items_to_compress) == 1:
                        default_name = Path(items_to_compress[0]).stem
                    else:
                        default_name = "archive"
                    
                    archive_name, cancelled = get_text_input(
                        f"Archive name (without extension):",
                        current_path, items, selected, filter_ext,
                        initial_value=default_name
                    )
                    
                    if not cancelled and archive_name:
                        output_path = os.path.join(current_path, f"{archive_name}.{format_type}")
                        
                        # Compress
                        if format_type == 'zip':
                            success, msg = compress_to_zip(items_to_compress, output_path)
                        elif format_type == '7z':
                            success, msg = compress_to_7z(items_to_compress, output_path)
                        elif format_type == 'rar':
                            success, msg = compress_to_rar(items_to_compress, output_path)
                        
                        message = msg
                        
                        # Refresh directory
                        all_items = scan_directory(current_path)
                        all_items = sort_items(all_items, sort_mode, sort_reverse)
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                        selected_items.clear()
                        
                        # Recalculate layout
                        effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
                    else:
                        message = "Compression cancelled"
            else:
                message = "No items to compress"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'EXTRACT':
            # Extract archive
            if items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                
                if not is_dir and is_archive(name):
                    # Get extraction folder name
                    default_folder = Path(name).stem
                    
                    folder_name, cancelled = get_text_input(
                        f"Extract to folder:",
                        current_path, items, selected, filter_ext,
                        initial_value=default_folder
                    )
                    
                    if not cancelled and folder_name:
                        extract_path = os.path.join(current_path, folder_name)
                        
                        # Create extraction folder if not exists
                        os.makedirs(extract_path, exist_ok=True)
                        
                        # Extract
                        success, msg = extract_archive(full_path, extract_path)
                        message = msg
                        
                        # Refresh directory
                        all_items = scan_directory(current_path)
                        all_items = sort_items(all_items, sort_mode, sort_reverse)
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                        
                        # Recalculate layout
                        effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
                    else:
                        message = "Extraction cancelled"
                else:
                    message = "Selected item is not an archive file"
            
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
            
        elif key == 'BACKSPACE':
            # Naik ke parent directory
            new_path, new_items = go_to_parent(current_path)
            if new_path:
                current_path = new_path
                all_items = new_items
                all_items = sort_items(all_items, sort_mode, sort_reverse)
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                selected = 0
                current_page = 0
                selected_items.clear()  # Clear selection saat pindah directory
                message = "Moved to parent directory"
                
                # Recalculate layout
                effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
            else:
                message = "Already at root directory"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
            
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
                        current_page = 0
                        selected_items.clear()
                        message = "Moved to parent directory"
                        effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
                elif is_dir:
                    # Masuk ke folder
                    new_path, new_items = change_directory(full_path)
                    if new_path:
                        current_path = new_path
                        all_items = new_items
                        all_items = sort_items(all_items, sort_mode, sort_reverse)
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                        selected = 0
                        current_page = 0
                        selected_items.clear()
                        message = f"Opened: {name}"
                        effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
                    else:
                        message = f"Cannot access: {name}"
                else:
                    # Open file dengan aplikasi default
                    if open_file(full_path):
                        message = f"Opening: {name}"
                    else:
                        message = f"Cannot open: {name}"
                
                render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'SORT':
            new_sort, reverse, cancelled = show_sort_menu(current_path, sort_mode, filter_ext)
            if not cancelled:
                if reverse:
                    sort_reverse = not sort_reverse
                    message = f"Sort order reversed: {'Descending' if sort_reverse else 'Ascending'}"
                else:
                    sort_mode = new_sort
                    message = f"Sorted by: {sort_mode.title()}"
                all_items = sort_items(all_items, sort_mode, sort_reverse)
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                selected = 0
                current_page = 0
                selected_items.clear()
                effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key in ['SORT_NAME', 'SORT_SIZE', 'SORT_DATE', 'SORT_TYPE']:
            sort_map = {'SORT_NAME': 'name', 'SORT_SIZE': 'size', 'SORT_DATE': 'date', 'SORT_TYPE': 'type'}
            sort_mode = sort_map[key]
            sort_reverse = False
            message = f"Sorted by: {sort_mode.title()}"
            all_items = sort_items(all_items, sort_mode, sort_reverse)
            items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
            selected = 0
            current_page = 0
            selected_items.clear()
            effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'VIEW':
            new_view, cancelled = show_view_menu(current_path, view_mode, filter_ext, sort_mode)
            if not cancelled:
                view_mode = new_view
                message = f"View mode: {view_mode.title()}"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'COPY':
            if selected_items:
                clipboard_items = [items[idx][4] for idx in selected_items if idx < len(items) and items[idx][0] != ".."]
                if clipboard_items:
                    clipboard_mode = 'copy'
                    message = f"Copied {len(clipboard_items)} items to clipboard"
            elif items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                if name != "..":
                    clipboard_items = [full_path]
                    clipboard_mode = 'copy'
                    message = f"Copied to clipboard: {name}"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'CUT':
            if selected_items:
                clipboard_items = [items[idx][4] for idx in selected_items if idx < len(items) and items[idx][0] != ".."]
                if clipboard_items:
                    clipboard_mode = 'cut'
                    message = f"Cut {len(clipboard_items)} items to clipboard"
            elif items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                if name != "..":
                    clipboard_items = [full_path]
                    clipboard_mode = 'cut'
                    message = f"Cut to clipboard: {name}"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'PASTE':
            if clipboard_items:
                if len(clipboard_items) == 1:
                    if clipboard_mode == 'copy':
                        success, msg = copy_item(clipboard_items[0], current_path)
                    else:
                        success, msg = move_item(clipboard_items[0], current_path)
                        if success:
                            clipboard_items = []
                            clipboard_mode = None
                else:
                    if clipboard_mode == 'copy':
                        success, msg = copy_multiple_items(clipboard_items, current_path)
                    else:
                        success, msg = move_multiple_items(clipboard_items, current_path)
                        if success:
                            clipboard_items = []
                            clipboard_mode = None
                message = msg
                all_items = scan_directory(current_path)
                all_items = sort_items(all_items, sort_mode, sort_reverse)
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                selected_items.clear()
                effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
            else:
                message = "Clipboard is empty"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'RENAME':
            if selected_items:
                message = "Cannot rename multiple items. Please select only one item."
            elif items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                if name != "..":
                    new_name, cancelled = get_text_input(f"Rename '{name}' to:", current_path, items, selected, filter_ext, initial_value=name)
                    if not cancelled and new_name and new_name != name:
                        success, msg = rename_item(full_path, new_name)
                        message = msg
                        all_items = scan_directory(current_path)
                        all_items = sort_items(all_items, sort_mode, sort_reverse)
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                        effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
                    elif not cancelled:
                        message = "Rename cancelled"
                else:
                    message = "Cannot rename parent directory marker"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'DELETE_KEY' or key == 'DELETE':
            if selected_items:
                paths_to_delete = [items[idx][4] for idx in selected_items if idx < len(items) and items[idx][0] != ".."]
                if paths_to_delete:
                    confirmed = confirm_dialog(f"Delete {len(paths_to_delete)} items? This cannot be undone!", current_path, filter_ext)
                    if confirmed:
                        success, msg = delete_multiple_items(paths_to_delete)
                        message = msg
                        all_items = scan_directory(current_path)
                        all_items = sort_items(all_items, sort_mode, sort_reverse)
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                        selected_items.clear()
                        if selected >= len(items):
                            selected = max(0, len(items) - 1)
                        effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
            elif items and selected < len(items):
                name, is_dir, size, modified, full_path = items[selected]
                if name != "..":
                    confirmed = confirm_dialog(f"Delete {'folder' if is_dir else 'file'} '{name}'? This cannot be undone!", current_path, filter_ext)
                    if confirmed:
                        success, msg = delete_item(full_path)
                        message = msg
                        all_items = scan_directory(current_path)
                        all_items = sort_items(all_items, sort_mode, sort_reverse)
                        items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                        if selected >= len(items):
                            selected = max(0, len(items) - 1)
                        effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'NEW_FOLDER':
            folder_name, cancelled = get_text_input("New folder name:", current_path, items, selected, filter_ext)
            if not cancelled and folder_name:
                success, msg = create_folder(current_path, folder_name)
                message = msg
                all_items = scan_directory(current_path)
                all_items = sort_items(all_items, sort_mode, sort_reverse)
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
            elif not cancelled:
                message = "Folder creation cancelled"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'NEW_FILE':
            filename, cancelled = get_filename_input(current_path, filter_ext)
            if not cancelled and filename:
                success, msg = create_file(current_path, filename)
                message = msg
                all_items = scan_directory(current_path)
                all_items = sort_items(all_items, sort_mode, sort_reverse)
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
            elif not cancelled:
                message = "File creation cancelled"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'SEARCH':
            search_query, cancelled = search_mode_input(current_path, all_items, filter_ext)
            if not cancelled and search_query:
                from functions.search_filter import search_items
                items = search_items(all_items, search_query)
                selected = 0
                current_page = 0
                selected_items.clear()
                message = f"Search results: {len(items)} items found for '{search_query}'"
                filter_ext = ""
                effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
            else:
                items = filter_by_extension(all_items, filter_ext) if filter_ext else all_items
                message = "Search cancelled"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
        
        elif key == 'FILTER':
            new_filter, cancelled = filter_mode_input(current_path, all_items, filter_ext)
            if not cancelled:
                filter_ext = new_filter
                if filter_ext:
                    items = filter_by_extension(all_items, filter_ext)
                    selected = 0
                    current_page = 0
                    selected_items.clear()
                    message = f"Filtered by *.{filter_ext}: {len(items)} items"
                else:
                    items = all_items
                    selected = 0
                    current_page = 0
                    message = "Filter cleared"
                effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
            else:
                message = "Filter cancelled"
            render_ui(current_path, items, selected, message, filter_ext=filter_ext, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
            
        elif key == 'ESC':
            if selected_items:
                selected_items.clear()
                message = "Selection cleared"
            else:
                filter_ext = ""
                items = all_items
                selected = 0
                current_page = 0
                message = "Filter cleared"
                effective_columns, _, _ = calculate_layout_info(num_columns, len(items))
            render_ui(current_path, items, selected, message, clipboard_info=clipboard_info, sort_mode=sort_mode, view_mode=view_mode, selected_items=selected_items, num_columns=effective_columns, page=current_page)
            
        elif key == 'QUIT':
            clear_screen()
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()