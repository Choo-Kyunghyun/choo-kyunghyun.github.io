import os
import csv
import yt_dlp
import ctypes
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone

# Print the output to the text widget
def print_output(text):
    output_text.insert(tk.END, text)
    output_text.see(tk.END)

# Get metadata from YouTube URL
def get_metadata(youtube_url, cookie):
    ydl_opts = {
        "quiet": True,
        "simulate": True,
        "extract_flat": True,
        "skip_download": True,
        "force_generic_extractor": True,
        "extractor_args": {
            "youtube": {
                "youtube_include_dash_manifest": False
            }
        },
        "cookiefile": cookie,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(youtube_url, download=False)
    except yt_dlp.utils.DownloadError as e:
        print_output(f"Error: {e}\n")
        return {}
    return meta

# Select thumbnail URL
def select_thumbnail(thumbnails, square):
    best_thumbnail = None
    best_resolution = 0

    # Select the best square or non-square thumbnail
    for thumbnail in thumbnails:
        width = thumbnail.get("width", 0)
        height = thumbnail.get("height", 0)
        resolution = width * height
        if (square and width == height) or (not square):
            if resolution > best_resolution:
                best_resolution = resolution
                best_thumbnail = thumbnail["url"]

    # If no square thumbnail found, select the best non-square thumbnail
    if not best_thumbnail and square:
        return select_thumbnail(thumbnails, False)
    
    # Return the best thumbnail URL
    return best_thumbnail

# Filter metadata fields
def filter_meta(meta):
    metadata = {
        "track": meta.get("track", meta.get("title")),
        "artists": meta.get("artists", [meta.get("uploader")]),
        "album": meta.get("album"),
        "release_year": meta.get("release_year"),
        "duration_string": meta.get("duration_string"),
        "thumbnail": select_thumbnail(meta.get("thumbnails"), True),
        "url": meta.get("original_url", meta.get("webpage_url")),
        "channel_url": meta.get("channel_url"),
        "tags": meta.get("tags"),
    }
    if metadata["channel_url"] is not None:
        metadata["channel_url"] = metadata["channel_url"].replace("www", "music")
    return metadata

# Process a YouTube URL
def process_url(url, csv_writer, cookie):
    try:
        url = url.split("&si=", 1)[0] if "&si=" in url else url
        print_output(url + "\n")
        meta = filter_meta(get_metadata(url, cookie))
        csv_writer.writerow([value if value is not None and value != "" else "None" for value in meta.values()])
        return True
    except Exception as e:
        print_output(f"Error processing video URL {url}: {e}\n")
        return False

# Generate playlists
def generate_playlists(path_urls, path_cookie, path_playlists, block_cookie):
    # Open the input file
    try:
        with open(path_urls, "r", encoding="utf-8") as file_urls:
            urls = file_urls.readlines()
            if not urls:
                print_output(f"Please add the YouTube URLs to {path_urls} and run again.\n")
                return
    except FileNotFoundError:
        print_output(f"Please add the YouTube URLs to {path_urls} and run again.\n")
        return

    # Check the cookie
    if block_cookie:
        path_cookie = None
    else:
        try:
            with open(path_cookie, "r", encoding="utf-8"):
                pass
        except FileNotFoundError:
            print_output(f"{path_cookie} not found. Please add the cookie file and run again, or enable cookie blocking.\n")
            return

    # Open the playlists file
    count = 0
    with open(path_playlists, "a", encoding="utf-8", newline="") as file_playlists:
        csv_writer = csv.writer(file_playlists)
        for url in urls:
            # Strip the URL and skip empty lines or comments
            url = url.strip()
            if not url or url.startswith("#"):
                continue

            # If it is a playlist URL, extract video URLs and process them
            if "list=" in url:
                meta = get_metadata(url, path_cookie)
                video_urls = [video["url"] for video in meta["entries"]] if "entries" in meta else []
                for video_url in video_urls:
                    count += 1 if process_url(video_url, csv_writer, path_cookie) else 0
            # If it is a video URL, process it
            else:
                count += 1 if process_url(url, csv_writer, path_cookie) else 0

    # Print success message
    print_output(f"Metadata of {count} videos extracted and saved to {path_playlists}.\n")

# Extract URLs
def extract_urls(path_playlists, path_youtube_urls, col):
    try:
        count = 0
        with open(path_playlists, "r", encoding="utf-8") as file_playlists:
            reader = csv.reader(file_playlists)
            with open(path_youtube_urls, "a", encoding="utf-8") as file_youtube_urls:
                for row in reader:
                    if len(row) > col:
                        file_youtube_urls.write(row[col] + "\n")
                        count += 1
        print_output(f"Metadata of {count} videos extracted and saved to {path_youtube_urls}.\n")
    except FileNotFoundError:
        print_output(f"Playlists file not found.\n")

# Check duplicates in the playlists file based on the specified columns and print the results
def check_duplicates(path_playlists, cols):
    # Open the playlists file and check for duplicated rows
    try:
        with open(path_playlists, "r", encoding="utf-8") as file_playlists:
            reader = csv.reader(file_playlists)
            seen_sets = {col: set() for col in cols}
            duplicated_rows = set()

            for row_num, row in enumerate(reader, start=1):
                for col in cols:
                    if len(row) > col:
                        if row[col] in seen_sets[col]:
                            duplicated_rows.add((row_num, tuple(row[col] for col in cols if len(row) > col)))
                        else:
                            seen_sets[col].add(row[col])
    except FileNotFoundError:
        print_output(f"Playlists file not found.\n")
        return

    # Print the results
    duplicated_rows = list(duplicated_rows)
    if not duplicated_rows:
        print_output("No duplicated rows found.\n")
    else:
        print_output("Duplicated rows:\n")
        for row_num, row in duplicated_rows:
            print_output(f"Row {row_num}: {row}\n")
        print_output(f"Total: {len(duplicated_rows)} duplicated rows.\n")
    return

# Cookie Converter
def cookie_converter(path_cookie_chrome, path_cookie):
    # Read the Chrome cookie file
    try:
        with open(path_cookie_chrome, "r", encoding="utf-8") as input_file:
            lines = input_file.readlines()
            if not lines:
                print_output(f"{path_cookie_chrome} is empty. Please add the Chrome cookie file and run again.\n")
                return
    except FileNotFoundError:
        print_output(f"{path_cookie_chrome} not found. Please add the Chrome cookie file and run again.\n")
        return

    # Write the Netscape cookie file
    with open(path_cookie, "a", encoding="utf-8") as cookie_file:
        cookie_file.write("# Netscape HTTP Cookie File\n")

        # Process each line
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue

            # Split line into parts and extract cookie parts
            parts = line.split("\t")
            name = parts[0]
            value = parts[1]
            domain = parts[2] if parts[2].startswith(".") else "." + parts[2]
            path = parts[3]
            expires = "0" if parts[4] == "Session" else str(int(datetime.fromisoformat(parts[4]).replace(tzinfo=timezone.utc).timestamp()))
            http_only = "TRUE" if parts[6] == "✓" else "FALSE"

            # Write cookie to file
            cookie_file.write(f"{domain}\tTRUE\t{path}\t{http_only}\t{expires}\t{name}\t{value}\n")

    # Print success message
    print_output(f"Cookie data extracted and saved to {path_cookie}.\n")

# Run the command in a separate thread
def run_command(target, *args):
    threading.Thread(target=target, args=args).start()

# Open the text file with default application
def open_file(path):
    if not os.path.exists(path):
        open(path, "a").close()
    os.startfile(path)

# File paths
path_playlists = "playlists.csv"
path_cookie = "cookie-youtube.txt"
path_youtube_urls = "playlists-youtube-urls.txt"
path_cookie_chrome = "cookie-chrome.txt"

# Windows Scaling
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# Variables
color_bg = "#0d1117"
color_fg = "#c9d1d9"
font_default = ("Arial", 12)

# Root
root = tk.Tk()
root.title("Playlists Manager")
root.geometry("800x600")
root.configure(bg=color_bg)

# Styles
style = ttk.Style()
style.theme_create("dark", parent="alt", settings={
    "TNotebook": {
        "configure": {
            "tabmargins": [2, 5, 2, 0],
            "background": color_bg
        }
    },
    "TNotebook.Tab": {
        "configure": {
            "padding": [8, 10],
            "background": color_bg,
            "foreground": color_fg,
            "font": font_default
        },
        "map": {
            "background": [("selected", "#58a6ff")],
            "expand": [("selected", [1, 1, 1, 0])]
        },
    }
})

# Apply style
style.theme_use("dark")

# Title
title = tk.Label(root, text="Playlists Manager", font=("Arial", 24), bg=color_bg, fg=color_fg)
title.pack(pady=16)

# Container of tabs
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Generate tab
tab_generate = tk.Frame(notebook, bg=color_bg)
notebook.add(tab_generate, text="Generate")

# Add cookie block checkbox for generate tab
block_cookie = tk.BooleanVar()
chk_block_cookie = tk.Checkbutton(tab_generate, text="Block Cookie", variable=block_cookie, onvalue=True, offvalue=False, bg=color_bg, fg=color_fg, font=font_default)
chk_block_cookie.pack(pady=16)

# Add open urls button for generate tab
btn_open_urls = tk.Button(tab_generate, text="Open YouTube URLs", command=lambda: run_command(open_file, path_youtube_urls), bg=color_bg, fg=color_fg, font=font_default)
btn_open_urls.pack(pady=16)

# Add generate button for generate tab
btn_generate = tk.Button(tab_generate, text="Generate Playlists", command=lambda: run_command(generate_playlists, path_youtube_urls, path_cookie, path_playlists, block_cookie.get()), bg=color_bg, fg=color_fg, font=font_default)
btn_generate.pack(pady=16)

# Add open playlists button for generate tab
btn_open_playlists = tk.Button(tab_generate, text="Open Playlists", command=lambda: run_command(open_file, path_playlists), bg=color_bg, fg=color_fg, font=font_default)
btn_open_playlists.pack(pady=16)

# Extract URLs tab
tab_extract = tk.Frame(notebook, bg=color_bg)
notebook.add(tab_extract, text="Extract URLs")

# Add extract button for extract tab
btn_extract = tk.Button(tab_extract, text="Extract URLs", command=lambda: run_command(extract_urls, path_playlists, path_youtube_urls, 6), bg=color_bg, fg=color_fg, font=font_default)
btn_extract.pack(pady=16)

# Add open urls button for extract tab
btn_open_urls = tk.Button(tab_extract, text="Open YouTube URLs", command=lambda: run_command(open_file, path_youtube_urls), bg=color_bg, fg=color_fg, font=font_default)
btn_open_urls.pack(pady=16)

# Check duplicates tab
tab_check = tk.Frame(notebook, bg=color_bg)
notebook.add(tab_check, text="Check Duplicates")

# Add check button for check tab
btn_check = tk.Button(tab_check, text="Check Duplicates", command=lambda: run_command(check_duplicates, path_playlists, [6]), bg=color_bg, fg=color_fg, font=font_default)
btn_check.pack(pady=16)

# Add check duplicates title for check tab
btn_check = tk.Button(tab_check, text="Check Duplicates Titles", command=lambda: run_command(check_duplicates, path_playlists, [0]), bg=color_bg, fg=color_fg, font=font_default)
btn_check.pack(pady=16)

# Cookie Converter tab
tab_cookie = tk.Frame(notebook, bg=color_bg)
notebook.add(tab_cookie, text="Cookie Converter")

# Add open chrome cookie button for check tab
btn_open_cookie = tk.Button(tab_cookie, text="Open Chrome Cookie", command=lambda: run_command(open_file, path_cookie_chrome), bg=color_bg, fg=color_fg, font=font_default)
btn_open_cookie.pack(pady=16)

# Add convert cookie button for cookie tab
btn_convert_cookie = tk.Button(tab_cookie, text="Convert Cookie", command=lambda: run_command(cookie_converter, path_cookie_chrome, path_cookie), bg=color_bg, fg=color_fg, font=font_default)
btn_convert_cookie.pack(pady=16)

# Add open cookie button for cookie tab
btn_open_cookie = tk.Button(tab_cookie, text="Open Cookie", command=lambda: run_command(open_file, path_cookie), bg=color_bg, fg=color_fg, font=font_default)
btn_open_cookie.pack(pady=16)

# Add Output widget
output_text = tk.Text(root, bg=color_bg, fg=color_fg, font=font_default, wrap="word")
output_text.pack(fill="both", expand=True)

# Main loop
root.mainloop()
