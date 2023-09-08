import requests
from bs4 import BeautifulSoup
import re

# Define custom headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/json',
    'Origin': 'https://www.mxplayer.in',
    'Connection': 'keep-alive',
    'Referer': 'https://www.mxplayer.in/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

# Function to extract data-tab value and show name from the provided URL
def extract_data_tab_and_show_name(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract data-tab value
        div_elements = soup.find_all('div', class_='tab-header')
        data_tab_values = [div.get('data-tab') for div in div_elements]
        
        # Extract show name from the URL
        show_name_match = re.search(r'watch-(.*?)-', url)
        if show_name_match:
            show_name = show_name_match.group(1)
            return data_tab_values, show_name

    return None, None

# Function to map data-tab values to season numbers
def map_data_tab_to_season(data_tab_value, data_tab_values):
    # Use the order in which data-tab values appear as season numbers
    if data_tab_value in data_tab_values:
        season_number = str(data_tab_values.index(data_tab_value) + 1)
    else:
        # If data-tab value not found, use the original value
        season_number = data_tab_value
    return season_number

# Function to map data-tab values to season names
def map_data_tab_to_season_name(data_tab_value):
    return data_tab_value

# Function to get all episodes and their names for a given API URL
def get_all_episodes(api_url):
    all_episodes = []

    while api_url:
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
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
                        all_episodes.append((episode_name, full_m3u8_link))
                else:
                    full_m3u8_link = "https://media-content.akamaized.net/" + high
                    episode_name = item.get("title", f"Episode {index}")
                    all_episodes.append((episode_name, full_m3u8_link))

            next_page = data.get("next")
            if next_page:
                # Extract the season_id from the current URL
                season_id = api_url.split("id=")[1].split("&")[0]

                # Map the data-tab value to the season number and season name
                season_number = map_data_tab_to_season(season_id, data_tab_values)
                season_name = map_data_tab_to_season_name(season_id)

                # Update the API URL with the new season_id and next_page
                api_url = f"https://api.mxplayer.in/v1/web/detail/tab/tvshowepisodes?type=season&id={season_id}&device-density=3&userid=d5e64bb6-7701-4dbe-a0d6-9a3eef12cf1e&platform=com.mxplay.desktop&content-languages=hi,en&kids-mode-enabled=false&{next_page}"
            else:
                api_url = None
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            api_url = None

    return all_episodes

# Take a list of season URLs as input from the user
season_urls = []
while True:
    url = input("Enter a season URL (or leave empty to finish): ").strip()
    if not url:
        break
    season_urls.append(url)

# Create a list to store all episode links and names
all_episodes = []

for season_url in season_urls:
    data_tab_values, show_name = extract_data_tab_and_show_name(season_url)

    if data_tab_values:
        for data_tab_value in data_tab_values:
            api_url = f"https://api.mxplayer.in/v1/web/detail/tab/tvshowepisodes?type=season&id={data_tab_value}&device-density=3&userid=d5e64bb6-7701-4dbe-a0d6-9a3eef12cf1e&platform=com.mxplay.desktop&content-languages=hi,en&kids-mode-enabled=false"

            season_episodes = get_all_episodes(api_url)

            if season_episodes:
                # Map the data-tab value to season number and season name
                season_number = map_data_tab_to_season(data_tab_value, data_tab_values)
                season_name = map_data_tab_to_season_name(data_tab_value)
                
                print(f"Show: {show_name}, Season {season_number} ({season_name}) Episodes:")
                for index, (episode_name, link) in enumerate(season_episodes, start=1):
                    print(f"Episode {index} - {episode_name}")
                    all_episodes.append((show_name, season_number, episode_name, link))
            else:
                print(f"No episode links found for Show: {show_name}, Season {data_tab_value} ({data_tab_value}).")
    else:
        print("Failed to extract data-tab values and show name from the provided URL.")

# Write all episode links and names to a text file
with open("episode_links.txt", "w") as file:
    for show_name, season_number, episode_name, link in all_episodes:
        file.write(f"Show: {show_name}, Season {season_number}, Episode {episode_name}, M3U8 Link: {link}\n")

print("All episode links and names have been exported to episode_links.txt.")
