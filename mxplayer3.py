import requests
from bs4 import BeautifulSoup

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

# Function to extract data-tab value from the provided URL
def extract_data_tab_value(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        div_elements = soup.find_all('div', class_='tab-header')
        data_tab_values = [div.get('data-tab') for div in div_elements]
        return data_tab_values
    return None

def get_all_episodes(api_url):
    all_episodes = []

    while api_url:
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])

            for item in items:
                stream = item.get("stream", {})
                hls = stream.get("hls", {})
                high = hls.get("high")

                if not high:
                    base = hls.get("base")
                    if base:
                        full_m3u8_link = "https://media-content.akamaized.net/" + base
                        all_episodes.append(full_m3u8_link)
                else:
                    full_m3u8_link = "https://media-content.akamaized.net/" + high
                    all_episodes.append(full_m3u8_link)

            next_page = data.get("next")
            if next_page:
                # Extract the season_id from the current URL
                season_id = api_url.split("id=")[1].split("&")[0]

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

# Create a list to store all episode links
all_episode_links = []

for season_url in season_urls:
    data_tab_values = extract_data_tab_value(season_url)

    if data_tab_values:
        for data_tab_value in data_tab_values:
            api_url = f"https://api.mxplayer.in/v1/web/detail/tab/tvshowepisodes?type=season&id={data_tab_value}&device-density=3&userid=d5e64bb6-7701-4dbe-a0d6-9a3eef12cf1e&platform=com.mxplay.desktop&content-languages=hi,en&kids-mode-enabled=false"

            all_episodes = get_all_episodes(api_url)

            if all_episodes:
                print(f"Season {data_tab_value} Episodes:")
                for index, link in enumerate(all_episodes, start=1):
                    print(f"Episode {index} M3U8 Link:", link)
                    all_episode_links.append(link)
            else:
                print(f"No episode links found for Season {data_tab_value}.")
    else:
        print("Failed to extract data-tab values from the provided URL.")

# Write all episode links to a text file
with open("episode_links.txt", "w") as file:
    for link in all_episode_links:
        file.write(link + "\n")

print("All episode links have been exported to episode_links.txt.")
