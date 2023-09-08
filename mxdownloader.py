import os
import subprocess
import re

# Read episode information from episode_links.txt
with open('episode_links.txt', 'r') as file:
    episode_info = file.read().splitlines()

# Regular expression pattern to match the required information
pattern = r"Show: (.*), Season (\d+), Episode (\d+), (.*), M3U8 Link: (.*)"

# Loop through each line in episode_info
for line in episode_info:
    match = re.match(pattern, line)
    if match:
        show, season, episode, episode_name, m3u8_link = match.groups()

        # Define the output file name
        output_file = f"{show.replace(' ', '_')}.S{season}.E{episode}.{episode_name.replace(' ', '_')}.mp4"

        # Use yt-dlp to download the M3U8 link and convert it to mp4
        subprocess.run([
            'yt-dlp',
            '-o', output_file,
            m3u8_link
        ])
    else:
        print(f"Invalid format: {line}")

print("Downloads completed successfully.")
