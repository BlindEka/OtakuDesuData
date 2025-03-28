from otakudesudata.parser import SearchResultParser, Parser, OngoingParser
from otakudesudata.constants import *
from bs4 import BeautifulSoup as bs
import httpx
import random


class SearchTypes:
  anime = 'anime'
  batch = 'batch'
  episode = 'episode'
  all = None


def search(query: str, search_type: SearchTypes=SearchTypes.anime, timeout=10, proxy=None, **kwargs):
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
      - update_details (bool, optional): whether to update each anime details during fetching anime details
      - client_max_connections (int, optional): The maximum number of client concurrent connections that may be established during fetching other details. Default to 100
      - max_keepalive_connections (int, optional): Allow the connection pool to maintain keep-alive connections below this point. Should be less than or equal to `client_max_connections`. Default to 20% of `client_max_connections`.
      - keepalive_expiry (float, optional): Time limit on idle keep-alive connections in seconds. Default to 5 seconds.
      - raise_exception (bool, optional): Whether to raise exceptions while fetching additional details. Defaults to False.

  Returns:
    dictionary: A dictionary of parsed search results.  containing:
      - anime list
      - episodes list
      - batch list

  Example:
    ```python
    from otakudesudata import search, SearchTypes

    # Search for anime
    results = search("One Piece", search_type=SearchTypes.anime)
    print(results['anime'])

    # Search for episodes
    results = search("One Piece Episode 1000", search_type=SearchTypes.episode)
    print(results['episodes'])

    # Search for batch downloads
    results = search("One Piece Batch", search_type=SearchTypes.batch)
    print(results['batch'])

      # Search for all types
    results = search("One Piece", search_type=SearchTypes.all)
    print(results['anime'])
    print(results['episodes'])
    print(results['batch'])
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
  parser = SearchResultParser(r.text, timeout=timeout, proxy=proxy, **kwargs)
  return parser.results

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
    from otakudesudata import get_ongoing

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

  Example:
    >>> from otakudesudata import get_schedules
    >>> schedules = get_schedules()
    >>> # Print the anime schedule for Monday
    >>> print(schedules['monday'])
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
    >>>from otakudesudata import get_anime_list
    >>> anime_list = get_anime_list(user_agent="CustomUserAgent", timeout=15)
    >>> # Print the first anime title and URL
    >>> print(f"Title: {anime_list[0]['title']}, URL: {anime_list[0]['url']}")
    
    # Output:
    [{'title': 'Anime Title 1', 'url': 'https://otakudesu.cloud/anime1'}, ...]
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
