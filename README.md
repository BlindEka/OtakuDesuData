# OtakuDesuData

OtakuDesuData is a Python module designed for scraping data from the [OtakuDesu](https://otakudesu.cloud) website, a free anime-sharing site with Indonesian subtitles. This module allows you to retrieve information such as anime lists, episodes, batch downloads, release schedules, and more.
## Features
- **Anime Search**: Search for anime by query.
- **Episode Search**: Search for episodes by query.
- **Batch Search**: Search for batch downloads of specific anime.
- **Release Schedules**: Retrieve anime release schedules.
- **Ongoing Anime**: Get a list of currently airing anime.
- **Anime Details**: Retrieve detailed information about a specific anime, including synopsis, genres, and more.
- **Episode Details**: Get detailed information about specific episodes, such as download links and release date.
- **Batch Details**: Retrieve detailed information about batch downloads, including available resolutions and download links.
- **Anime List**: Retrieve a paginated list of all available anime on the website.
- **Custom Parsers**: Use built-in parsers to extract specific data from OtakuDesu pages.
- **asynchronus operation**: get every anime, episode and batch details on search results at the same time with asynchronus operations.


## Installation
You can install this module directly from GitHub using the following command:
```bash
pip install git+https://github.com/BlindEka/OtakuDesuData.git
```
Usage Examples
Here are some examples of how to use this module:
Anime Search

```
from otakudesudata import search, SearchTypes

# Search for anime by query
results = search("jujutsu kaisen", search_type=SearchTypes.anime)
#print all anime
for anime in results['anime']:
  print(f"title: {anime['title']}")
  print(f"url: {anime['url']}")
  print(f"status: {anime['status']}")
  print(f"rating: {anime['rating']}")
  ...
```
Episode Search

```
from otakudesudata import search, SearchTypes

# Search for episodes by title or episode number
results = search("jujutsu kaisen episode 10", search_type=SearchTypes.episode)
#print all episodes
for episode in results['episodes']:
  print(f"title: {episode['title']}")
  print(f"url: {episode['url']}")
```
Batch Search

```
from otakudesudata import search, SearchTypes

# Search for batch downloads of specific anime
results = search("jujutsu kaisen season 1", search_type=SearchTypes.batch)
#print all anime batches
for batch in results['batch']:
  print(f"title: {batch['title']}")
  print(f"url: {batch['url']}")
```
Get Ongoing Anime

```
from otakudesudata import get_ongoing

# Get a list of currently airing anime
ongoing_anime = get_ongoing(get_all=True) #get all ongoing anime from all page
for anime in ongoing_anime:
  print(f"title: {anime['title']}")
  print(f"url: {anime['url']})
```
Get Release Schedules

```
from otakudesudata import get_schedules

# Retrieve anime release schedules
schedules = get_schedules()
#print schedule for sunday
print(schedules['sunday'])
```
Contribution
Contributions are welcome! If you find any bugs or have ideas for new features, feel free to create an issue or a pull request in this repository.
License
This project is licensed under the [MIT License](LICENSE).

