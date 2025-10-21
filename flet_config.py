# Flet configuration file
import os

# Include additional files in the build
def get_include_files():
    """Return list of files to include in the build"""
    include_files = []
    
    # Database file
    if os.path.exists("product_data.db"):
        include_files.append("product_data.db")
    
    # Settings file
    if os.path.exists("settings.json"):
        include_files.append("settings.json")
    
    # Preview directory
    if os.path.exists("preview"):
        include_files.append("preview")
    
    # Processed directory
    if os.path.exists("processed"):
        include_files.append("processed")
    
    # Watch folder directory
    if os.path.exists("watch_folder"):
        include_files.append("watch_folder")
    
    # Storage directory
    if os.path.exists("storage"):
        include_files.append("storage")
    
    return include_files

# Export the configuration
__all__ = ["get_include_files"]

