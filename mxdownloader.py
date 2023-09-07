import os
import yt_dlp

# Function to download videos from a list of links using yt-dlp
def download_videos(links, output_dir):
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for link in links:
            ydl.download([link])

# Specify the path to the episode_links.txt file
links_file = 'episode_links.txt'

# Specify the output directory where videos will be downloaded
output_directory = 'downloaded_videos'

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

try:
    with open(links_file, 'r') as file:
        episode_links = file.read().splitlines()

    if episode_links:
        print(f"Downloading {len(episode_links)} videos...")
        download_videos(episode_links, output_directory)
        print("Download completed.")
    else:
        print("No episode links found in the file.")
except FileNotFoundError:
    print(f"The file {links_file} does not exist.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
