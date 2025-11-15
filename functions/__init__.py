"""
File Explorer Functions Package
"""

from .keyboard import get_key
from .ui import (
    clear_screen,
    get_terminal_size,
    draw_header,
    draw_footer,
    render_ui
)
from .file_system import (
    format_size,
    get_file_info,
    scan_directory,
    open_file,
    change_directory,
    go_to_parent
)
from .file_operations import (
    copy_item,
    move_item,
    delete_item,
    rename_item,
    create_folder,
    create_file,
    copy_multiple_items,
    move_multiple_items,
    delete_multiple_items
)
from .sorting import (
    sort_items,
    show_sort_menu,
    show_view_menu,
    format_item_display
)
from .search_filter import (
    search_items,
    filter_by_extension,
    search_mode_input,
    filter_mode_input
)
from .dialogs import (
    get_text_input,
    get_filename_input,
    confirm_dialog
)
from .compression import (
    is_archive,
    compress_to_zip,
    compress_to_7z,
    compress_to_rar,
    extract_archive,
    show_compression_menu
)
from .layout import (
    show_layout_menu
)

__all__ = [
    # Keyboard
    'get_key',
    
    # UI
    'clear_screen',
    'get_terminal_size',
    'draw_header',
    'draw_footer',
    'render_ui',
    
    # File System
    'format_size',
    'get_file_info',
    'scan_directory',
    'open_file',
    'change_directory',
    'go_to_parent',
    
    # File Operations
    'copy_item',
    'move_item',
    'delete_item',
    'rename_item',
    'create_folder',
    'create_file',
    'copy_multiple_items',
    'move_multiple_items',
    'delete_multiple_items',
    
    # Sorting
    'sort_items',
    'show_sort_menu',
    'show_view_menu',
    'format_item_display',
    
    # Search & Filter
    'search_items',
    'filter_by_extension',
    'search_mode_input',
    'filter_mode_input',
    
    # Dialogs
    'get_text_input',
    'get_filename_input',
    'confirm_dialog',
    
    # Compression
    'is_archive',
    'compress_to_zip',
    'compress_to_7z',
    'compress_to_rar',
    'extract_archive',
    'show_compression_menu',
    
    # Layout
    'show_layout_menu',
]