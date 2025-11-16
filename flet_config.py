# Flet configuration file
import os

# Include additional files in the build
def get_include_files():
    """Return list of files to include in the build
    Returns list of tuples: (source_path, destination_path)
    For PyInstaller/flet pack, use format: (source, destination)
    """
    include_files = []
    
    # Database file
    if os.path.exists("product_data.db"):
        include_files.append(("product_data.db", "."))
    
    # Settings file
    if os.path.exists("settings.json"):
        include_files.append(("settings.json", "."))
    
    # Manual file - 明示的に追加
    if os.path.exists("MENU_MANUAL.md"):
        include_files.append(("MENU_MANUAL.md", "."))
    
    # Preview directory
    if os.path.exists("preview"):
        include_files.append(("preview", "preview"))
    
    # Processed directory
    if os.path.exists("processed"):
        include_files.append(("processed", "processed"))
    
    # Watch folder directory
    if os.path.exists("watch_folder"):
        include_files.append(("watch_folder", "watch_folder"))
    
    # Storage directory
    if os.path.exists("storage"):
        include_files.append(("storage", "storage"))
    
    return include_files

# Export the configuration
__all__ = ["get_include_files"]

