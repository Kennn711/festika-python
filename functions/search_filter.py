"""
Search and filter functions
"""
import msvcrt
from pathlib import Path
from .ui import render_ui


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