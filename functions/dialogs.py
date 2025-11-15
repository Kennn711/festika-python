"""
Input dialog functions
"""
import msvcrt
from .ui import clear_screen, draw_header, get_terminal_size


def get_text_input(prompt, current_path, items, selected, filter_ext, initial_value=""):
    """Get text input dari user"""
    text = initial_value
    
    # Render dengan input prompt
    clear_screen()
    cols, _ = get_terminal_size()
    
    draw_header(current_path, filter_ext=filter_ext)
    print(f"\n {prompt}")
    print(f" > {text}_")
    print("\n [Enter: Confirm | ESC: Cancel]")
    
    while True:
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter
            return text, False
        elif key == b'\x1b':  # ESC
            return "", True
        elif key == b'\x08':  # Backspace
            if text:
                text = text[:-1]
        elif key == b'\xe0':  # Skip special keys
            msvcrt.getch()
            continue
        else:
            try:
                char = key.decode('utf-8')
                if char.isprintable():
                    text += char
            except:
                continue
        
        # Re-render
        clear_screen()
        draw_header(current_path, filter_ext=filter_ext)
        print(f"\n {prompt}")
        print(f" > {text}_")
        print("\n [Enter: Confirm | ESC: Cancel]")


def get_filename_input(current_path, filter_ext):
    """Get filename dengan extension dari user (2 step input)"""
    
    # Step 1: Input nama file
    clear_screen()
    draw_header(current_path, filter_ext=filter_ext)
    print(f"\n 📝 Create New File")
    print(f"\n Step 1: Enter filename (without extension)")
    print(f" > _")
    print("\n [Enter: Next | ESC: Cancel]")
    
    filename = ""
    while True:
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter - lanjut ke step 2
            if filename:
                break
            else:
                continue
        elif key == b'\x1b':  # ESC
            return "", True
        elif key == b'\x08':  # Backspace
            if filename:
                filename = filename[:-1]
        elif key == b'\xe0':  # Skip special keys
            msvcrt.getch()
            continue
        else:
            try:
                char = key.decode('utf-8')
                # Hanya izinkan karakter valid untuk nama file
                if char.isprintable() and char not in ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '.']:
                    filename += char
            except:
                continue
        
        # Re-render
        clear_screen()
        draw_header(current_path, filter_ext=filter_ext)
        print(f"\n 📝 Create New File")
        print(f"\n Step 1: Enter filename (without extension)")
        print(f" > {filename}_")
        print("\n [Enter: Next | ESC: Cancel]")
    
    # Step 2: Input extension
    clear_screen()
    draw_header(current_path, filter_ext=filter_ext)
    print(f"\n 📝 Create New File")
    print(f"\n Filename: {filename}")
    print(f"\n Step 2: Enter file extension (e.g., txt, py, json)")
    print(f" > ._")
    print("\n [Enter: Create | ESC: Cancel]")
    print("\n Common extensions: txt, py, json, md, html, css, js, xml, csv")
    
    extension = ""
    while True:
        key = msvcrt.getch()
        
        if key == b'\r':  # Enter - create file
            # Jika tidak ada extension, default ke .txt
            if not extension:
                extension = "txt"
            break
        elif key == b'\x1b':  # ESC
            return "", True
        elif key == b'\x08':  # Backspace
            if extension:
                extension = extension[:-1]
        elif key == b'\xe0':  # Skip special keys
            msvcrt.getch()
            continue
        else:
            try:
                char = key.decode('utf-8')
                # Hanya izinkan alphanumeric untuk extension
                if char.isalnum():
                    extension += char
            except:
                continue
        
        # Re-render
        clear_screen()
        draw_header(current_path, filter_ext=filter_ext)
        print(f"\n 📝 Create New File")
        print(f"\n Filename: {filename}")
        print(f"\n Step 2: Enter file extension (e.g., txt, py, json)")
        print(f" > .{extension}_")
        print("\n [Enter: Create | ESC: Cancel]")
        print("\n Common extensions: txt, py, json, md, html, css, js, xml, csv")
    
    # Gabungkan filename dan extension
    full_filename = f"{filename}.{extension}"
    return full_filename, False


def confirm_dialog(message, current_path, filter_ext):
    """Confirmation dialog (Y/N)"""
    clear_screen()
    cols, _ = get_terminal_size()
    
    draw_header(current_path, filter_ext=filter_ext)
    print(f"\n ⚠️  {message}")
    print("\n [Y: Yes | N: No]")
    
    while True:
        key = msvcrt.getch()
        
        if key == b'y' or key == b'Y':
            return True
        elif key == b'n' or key == b'N' or key == b'\x1b':
            return False