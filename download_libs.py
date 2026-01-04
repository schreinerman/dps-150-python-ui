#!/usr/bin/env python3
"""
Download script for all JavaScript/CSS libraries
Downloads all CDN dependencies to static/libs/ for offline use
"""

import os
import sys
import urllib.request
from pathlib import Path

# Libraries to download
LIBRARIES = {
    # Vue.js
    'vue.global.min.js': 'https://cdn.jsdelivr.net/npm/vue@3.5.13/dist/vue.global.min.js',
    
    # Vuetify
    'vuetify.min.js': 'https://cdn.jsdelivr.net/npm/vuetify@3.7.4/dist/vuetify.min.js',
    'vuetify.min.css': 'https://cdn.jsdelivr.net/npm/vuetify@3.7.4/dist/vuetify.min.css',
    
    # Plotly.js
    'plotly.min.js': 'https://cdn.jsdelivr.net/npm/plotly.js@2.35.2/dist/plotly.min.js',
    
    # Socket.IO
    'socket.io.min.js': 'https://cdn.socket.io/4.5.4/socket.io.min.js',
    
    # Material Design Icons CSS
    'materialdesignicons.min.css': 'https://cdn.jsdelivr.net/npm/@mdi/font@7.4.47/css/materialdesignicons.min.css',
}

# Font files (from Material Design Icons)
FONTS = {
    'materialdesignicons-webfont.woff2': 'https://cdn.jsdelivr.net/npm/@mdi/font@7.4.47/fonts/materialdesignicons-webfont.woff2',
    'materialdesignicons-webfont.woff': 'https://cdn.jsdelivr.net/npm/@mdi/font@7.4.47/fonts/materialdesignicons-webfont.woff',
    'materialdesignicons-webfont.ttf': 'https://cdn.jsdelivr.net/npm/@mdi/font@7.4.47/fonts/materialdesignicons-webfont.ttf',
}

def download_file(url, dest_path):
    """Download a file from URL to destination path"""
    print(f"  Downloading {dest_path.name}...", end=' ')
    try:
        urllib.request.urlretrieve(url, dest_path)
        size = dest_path.stat().st_size / 1024  # KB
        print(f"✓ ({size:.1f} KB)")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Main function"""
    print("=== Downloading JavaScript/CSS Libraries ===\n")
    
    # Create directories
    libs_dir = Path('static/libs')
    fonts_dir = Path('static/libs/fonts')
    libs_dir.mkdir(parents=True, exist_ok=True)
    fonts_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Target directory: {libs_dir.absolute()}\n")
    
    # Download libraries
    print("Downloading libraries:")
    success_count = 0
    for filename, url in LIBRARIES.items():
        dest = libs_dir / filename
        if download_file(url, dest):
            success_count += 1
    
    # Download fonts
    print("\nDownloading fonts:")
    for filename, url in FONTS.items():
        dest = fonts_dir / filename
        if download_file(url, dest):
            success_count += 1
    
    # Update CSS file to use local fonts
    css_file = libs_dir / 'materialdesignicons.min.css'
    if css_file.exists():
        print("\nUpdating font paths in CSS...", end=' ')
        content = css_file.read_text()
        # Replace CDN font paths with local paths
        content = content.replace('../fonts/', 'fonts/')
        content = content.replace('https://cdn.jsdelivr.net/npm/@mdi/font@7.4.47/fonts/', 'fonts/')
        css_file.write_text(content)
        print("✓")
    
    # Summary
    total = len(LIBRARIES) + len(FONTS)
    print(f"\n=== Download Complete ===")
    print(f"Successfully downloaded: {success_count}/{total} files")
    
    if success_count == total:
        print("\n✓ All files downloaded successfully!")
        print("\nNext steps:")
        print("  The index.html file will be updated to use local libraries.")
        return 0
    else:
        print(f"\n⚠️  Warning: {total - success_count} files failed to download")
        return 1

if __name__ == '__main__':
    sys.exit(main())
