import os
from pathlib import Path

# Import semua functions dari package
from functions import (
    # Keyboard
    get_key,
    
    # UI
    clear_screen,
    render_ui,
    
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
)


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
                from functions.search_filter import search_items
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