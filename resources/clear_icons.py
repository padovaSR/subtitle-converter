import os
import re

# Define the directory paths
icon_directory = os.path.join('resources', 'icons')
current_directory = os.getcwd()

# Regular expression to match icon file names (with .png or .ico extensions)
# This pattern allows for dots, numbers, hyphens, and underscores in the icon names
icon_pattern = re.compile(r'[\'\"]([a-zA-Z0-9_\-\.]+?\.(?:png|ico))[\'\"]')

def find_used_icons():
    used_icons = set()

    # Walk through all .py files in the current directory
    for root, _, files in os.walk(current_directory):
        for file in files:
            if file.endswith('.py'):
                py_file_path = os.path.join(root, file)
                with open(py_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    icons_found = icon_pattern.findall(content)
                    used_icons.update(icons_found)
    
    return used_icons

def find_available_icons():
    available_icons = set()

    # List all .png and .ico files in the resources/icons directory
    if os.path.exists(icon_directory):
        for root, _, files in os.walk(icon_directory):
            for file in files:
                if file.endswith(('.png', '.ico')):
                    available_icons.add(file)

    return available_icons

def delete_unused_icons(used_icons, available_icons):
    unused_icons = available_icons - used_icons

    # Delete all unused icons
    for icon in unused_icons:
        icon_path = os.path.join(icon_directory, icon)
        try:
            os.remove(icon_path)
            print(f"Deleted unused icon: {icon}")
        except OSError as e:
            print(f"Error deleting {icon}: {e}")

if __name__ == '__main__':
    # Step 1: Find used icons in the .py files
    used_icons = find_used_icons()
    print(f"Used icons: {used_icons}")

    # Step 2: Find available icons in the resources/icons directory
    available_icons = find_available_icons()
    print(f"Available icons: {available_icons}")

    # Step 3: Delete unused icons
    delete_unused_icons(used_icons, available_icons)
