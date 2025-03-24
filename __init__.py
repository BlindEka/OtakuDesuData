from OtakuDesuData.parser import SearchResultParser, Parser, OngoingParser
from OtakuDesuData.constants import *
from bs4 import BeautifulSoup as bs
import httpx
import random


class SearchTypes:
  anime = 'anime'
  batch = 'batch'
  episode = 'episode'
  all = None


def search(query: str, search_type: SearchTypes=SearchTypes.anime, timeout=10, proxy=None, **kwargs):
  def search(query: str, search_type: SearchTypes = SearchTypes.anime, timeout=10, proxy=None, **kwargs):
    """
    Searches for anime, episodes, or batch data on the OtakuDesu website.

    Args:
      query (str): The search query string to look for.
      search_type (SearchTypes, optional): The type of search to perform. Defaults to `SearchTypes.anime`.
        - `SearchTypes.anime`: Search for anime titles.
        - `SearchTypes.episode`: Search for episodes.
        - `SearchTypes.batch`: Search for batch downloads.
        - `SearchTypes.all`: Search for all types.
      timeout (int, optional): Timeout duration (in seconds) for the HTTP request. Defaults to 10.
      proxy (str, optional): Proxy URL to be used for the HTTP request. Defaults to None.
      **kwargs: Additional keyword arguments passed to `SearchResultParser`. These include:
        - user_agent (str, optional): Custom User-Agent header for the HTTP request. Defaults to a rotating user agent.
        - get_anime_detail (bool, optional): Whether to fetch detailed information for each anime. Defaults to False.
        - get_episode_details (bool, optional): Whether to fetch detailed information for each episode. Defaults to False.
        - get_batch_details (bool, optional): Whether to fetch detailed information for each batch. Defaults to False.
        - raise_exception (bool, optional): Whether to raise exceptions while fetching additional details. Defaults to False.

    Returns:
      list: A list of parsed search results. The structure of the results depends on the `search_type`:
        - For `SearchTypes.anime`: A list of dictionaries containing anime details such as title, URL, thumbnails, genres, status, and rating.
        - For `SearchTypes.episode`: A list of dictionaries containing episode details such as title, URL, and episode number.
        - For `SearchTypes.batch`: A list of dictionaries containing batch download details such as title and URL.

    Example:
      ```python
      from OtakuDesuData import search, SearchTypes

      # Search for anime
      results = search("One Piece", search_type=SearchTypes.anime)
      print(results)

      # Search for episodes
      results = search("One Piece Episode 1000", search_type=SearchTypes.episode)
      print(results)

      # Search for batch downloads
      results = search("One Piece Batch", search_type=SearchTypes.batch)
      print(results)

      # Search for all types
      results = search("One Piece", search_type=SearchTypes.all)
      ```
    """
  params = {'s': query, 'post_type': search_type} if search_type else {'s': query}
  r = httpx.get(
    baseUrl,
                timeout=timeout,
                params=params,
                proxy=proxy,
                headers={'User-Agent': kwargs.get('user_agent', random.choice(userAgents))}
                )
  results = SearchResultParser(r.text, timeout=timeout, proxy=proxy, **kwargs)
  return results.results

def get_ongoing(get_all: bool=False, use_cache: bool=True, timeout: int=10, proxy: str=None, **kwargs: dict):
  """
  Fetches the list of ongoing anime from the OtakuDesu website.

  Args:
    get_all (bool, optional): Whether to get all ongoing anime from all pages. Defaults to False.
    use_cache (bool, optional): Whether to use the cached data. Defaults to True.
    timeout (int, optional): Timeout duration (in seconds) for the HTTP request. Defaults to 10.
    proxy (str, optional): Proxy URL to be used for the HTTP request. Defaults to None.
      
  Returns:
    list: A list of parsed ongoing anime. Each item is a dictionary containing anime details such as title, URL, latestEpisode, thumbnails, and more.

  Example:
    ```python
    from OtakuDesuData import get_ongoing

    # Get the list of ongoing anime
    ongoing_anime = get_ongoing()
    print(ongoing_anime)
    ```
  """
  ongoing = OngoingParser(
    ongoingUrl,
    use_cache=use_cache,
    timeout=timeout,
    proxy=proxy,
    headers={'User-Agent': kwargs.get('user_agent', random.choice(userAgents))}
  )
  if not get_all: return ongoing
  results = []
  for release in ongoing:
    results.append(release)
  return results
  

def get_schedules(**kwargs: dict):
  """
  Retrieves the anime release schedules from the OtakuDesu website.

  This function sends an HTTP GET request to the schedules URL, parses the HTML response,
  and extracts the anime release schedules grouped by day. The result is returned as a dictionary
  where the keys are the days of the week and the values are lists of anime titles and their URLs.

  Parameters:
    **kwargs (dict): Optional keyword arguments to customize the request:
      - user_agent (str): A custom User-Agent string for the HTTP request. Defaults to a random choice from `userAgents`.
      - timeout (int): The timeout value for the HTTP request in seconds. Defaults to 10 seconds.
      - proxy (str): A proxy URL to use for the HTTP request. Defaults to None.

  Returns:
    dict: A dictionary where the keys are days of the week (e.g., "monday", "tuesday") + "random" and the values
    are lists of dictionaries containing:
      - 'title' (str): The title of the anime.
      - 'url' (str): The URL of the anime.

  Notes:
    - The function uses BeautifulSoup to parse the HTML response and extract the relevant data.
    - The `dayMapping` dictionary is used to map day names from the website to standardized day names.
    - If a day or anime title is not found, it will be skipped or set to None.

  Example:
    schedules = get_schedules(user_agent="CustomUserAgent", timeout=15)
    print(schedules["monday"])
  """
  response = httpx.get(schedulesUrl,
                       headers={'User-Agent': kwargs.get('user_agent', random.choice(userAgents))},
                       timeout=kwargs.get('timeout', 10),
                        proxy=kwargs.get('proxy'))
  soup = bs(response.text,'html.parser')
  return {
    dayMapping.get(day.h2.text.strip().lower(), day.h2.text.strip().lower()): [
      {
        'title': anime.text.strip() if anime.text else None,
        'url': anime.get('href')
      }
    for anime in day.find_all('a')]
   for day in soup.find_all('div', class_='kglist321')
   if day.h2}

def get_anime_list(**kwargs: dict)->list:
  def get_anime_list(**kwargs: dict) -> list:
    """
    Fetches a list of anime from the OtakuDesu website.

    This function sends an HTTP GET request to the anime list URL of the OtakuDesu website,
    parses the HTML response, and extracts the anime titles and their corresponding URLs.

    Args:
      **kwargs: Arbitrary keyword arguments.
        - user_agent (str, optional): A custom User-Agent string to use in the request headers.
          If not provided, a random User-Agent will be selected from the `userAgents` list.
        - timeout (int, optional): The timeout value for the HTTP request in seconds. Defaults to 10 seconds.
        - proxy (str, optional): A proxy URL to use for the HTTP request.

    Returns:
      list: A list of dictionaries, where each dictionary contains:
        - 'title' (str): The title of the anime.
        - 'url' (str): The URL of the anime.

    Example:
      >>>from OtakuDesuData import get_anime_list
      >>> anime_list = get_anime_list(user_agent="CustomUserAgent", timeout=15)
      >>> print(anime_list)
      # Output:
      [{'title': 'Anime Title 1', 'url': 'https://otakudesu.tv/anime1'}, ...]
    """
  response = httpx.get(animeListUrl,
                       headers={'User-Agent': kwargs.get('user_agent', random.choice(userAgents))},
                       timeout=kwargs.get('timeout', 10),
                        proxy=kwargs.get('proxy'))
  soup = bs(response.text,'html.parser')
  animeListElements = soup.find_all('a',class_='hodebgst')
  return [
    {
      'title': animeListElement.text.strip(),
      'url': animeListElement.get('href')
    }if animeListElement.text else None
  for animeListElement in animeListElements]
