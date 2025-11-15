"""
Keyboard input handling
"""
import msvcrt


def get_key():
    """Fungsi untuk menangkap input keyboard"""
    key = msvcrt.getch()
    
    # Arrow keys di Windows return 2 bytes
    if key == b'\xe0':  # Special key prefix
        key = msvcrt.getch()
        if key == b'H':    # Up arrow
            return 'UP'
        elif key == b'P':  # Down arrow
            return 'DOWN'
        elif key == b'K':  # Left arrow
            return 'LEFT'
        elif key == b'M':  # Right arrow
            return 'RIGHT'
        elif key == b'S':  # Delete key
            return 'DELETE'
    elif key == b'\r':     # Enter
        return 'ENTER'
    elif key == b'\x08':   # Backspace
        return 'BACKSPACE'
    elif key == b'/':      # Slash untuk search
        return 'SEARCH'
    elif key == b'f' or key == b'F':  # Filter
        return 'FILTER'
    elif key == b'c' or key == b'C':  # Copy
        return 'COPY'
    elif key == b'x' or key == b'X':  # Cut (move)
        return 'CUT'
    elif key == b'v' or key == b'V':  # Paste
        return 'PASTE'
    elif key == b'r' or key == b'R':  # Rename
        return 'RENAME'
    elif key == b'd' or key == b'D':  # Delete
        return 'DELETE_KEY'
    elif key == b'n' or key == b'N':  # New folder
        return 'NEW_FOLDER'
    elif key == b't' or key == b'T':  # New file
        return 'NEW_FILE'
    elif key == b's' or key == b'S':  # Sort menu
        return 'SORT'
    elif key == b'w' or key == b'W':  # View mode
        return 'VIEW'
    elif key == b'q' or key == b'Q':  # Quit
        return 'QUIT'
    elif key == b'\x1b':   # ESC
        return 'ESC'
    elif key == b' ':      # Spacebar untuk toggle selection
        return 'SPACE'
    elif key == b'a' or key == b'A':  # Select all
        return 'SELECT_ALL'
    elif key == b'1':      # Sort shortcuts
        return 'SORT_NAME'
    elif key == b'2':
        return 'SORT_SIZE'
    elif key == b'3':
        return 'SORT_DATE'
    elif key == b'4':
        return 'SORT_TYPE'
    
    return None