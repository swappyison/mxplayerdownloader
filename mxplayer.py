import requests
import subprocess
from pathlib import Path

all_episodes = []
seen_urls = set()
m3u8DL_RE = 'N_m3u8DL-RE'
show_name = input("enter show name:")
season_num = input("enter season number")
cookies = {
    #your cookies
}

headers = {
    #your headers
}
print('\ntest link:https://api.mxplayer.in/v1/web/detail/tab/aroundcurrentepisodes?type=season&id=ee03b94ccb07eccf00ce5f82c89ff44c&filterId=eeee5e4d7fdf623b143ecfb73683bb42&device-density=3&userid=d5e64bb6-7701-4dbe-a0d6-9a3eef12cf1e&platform=com.mxplay.desktop&content-languages=hi,en&kids-mode-enabled=false\n')

url = input("enter url:")
response = requests.get( url,
    cookies=cookies,
    headers=headers,
)
data = response.json()
items = data.get("items", [])
for index, item in enumerate(items, start=1):
    stream = item.get("stream", {})
    hls = stream.get("hls", {})
    high = hls.get("high")

    if not high:
        base = hls.get("base")
        if base:
            full_m3u8_link = "https://media-content.akamaized.net/" + base
            episode_name = item.get("title", f"Episode {index}")
    else:
        full_m3u8_link = "https://media-content.akamaized.net/" + high
        episode_name = item.get("title", f"Episode {index}")
    if full_m3u8_link not in seen_urls:
        all_episodes.append((episode_name, full_m3u8_link))
        seen_urls.add(full_m3u8_link)
    title = f'{show_name} - S{season_num}E{index}'


    for episode in seen_urls:
        subprocess.run([m3u8DL_RE,
                    '-M', 'format=mkv:muxer=ffmpeg',
                    '--concurrent-download',
                    '--log-level', 'INFO',
                    '-sv', 'best',
                    '-sa', 'best', '-ss', 'lang="en":for=all',
                    '--save-name', 'video',episode])
        try:

            Path('video.mkv').rename('' + title + '.mkv')
            print(f'{title}.mkv \nall done!\n')
        except FileNotFoundError:
            print("[ERROR] no mkv file")


