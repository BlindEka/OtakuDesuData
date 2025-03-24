from bs4 import BeautifulSoup as bs
from OtakuDesuData.constants import *
import re
import asyncio
import httpx
import random


class Parser:
  def __getitem__(self, key: str):
    if hasattr(self, key):
      return getattr(self, key)
    raise KeyError(key)

  @property
  def results(self):
    return vars(self)

class SearchResultParser(Parser):
  class SearchResultParser:
    """
    A parser class for extracting anime search results, episodes, and batch details from an HTML string.
    This class is designed to parse HTML content (from otakudesu search results page) and extract structured data such as anime details, 
    episode information, and batch download links. It also supports asynchronous operations for 
    fetching additional details using the provided keyword arguments.
    Attributes:
      anime (list): A list of dictionaries containing anime details such as title, URL, thumbnails, genres, status, and rating.
      episodes (list): A list of dictionaries containing episode details such as title, URL, and episode number.
      batch (list): A list of dictionaries containing batch download details such as title and URL.
    Methods:
      get_anime(soup: bs4.BeautifulSoup ) -> list:
        Extracts anime details from the provided BeautifulSoup object.
      get_episodes(soup: bs4.BeautifulSoup ) -> list:
        Extracts episode details from the provided BeautifulSoup object.
      get_batch(soup: bs4.BeautifulSoup ) -> list:
        Extracts batch download details from the provided BeautifulSoup object.
    Args:
      html_string (str): The HTML content to be parsed.
      **kwargs (dict): Additional keyword arguments for asynchronous operations. Supported arguments include:
        - proxy (str, optional): Proxy URL to be used for fetching additional details.
        - user_agent (str, optional): Custom user agent string. Defaults to a rotating user agent.
        - timeout (int, optional): Timeout duration (in seconds) for network requests. Defaults to a reasonable value.
        - get_anime_detail (bool, optional): Whether to fetch detailed information for each anime. Defaults to False.
        - get_episode_details (bool, optional): Whether to fetch detailed information for each episode. Defaults to False.
        - get_batch_details (bool, optional): Whether to fetch detailed information for each batch. Defaults to False.
        raise_exception (bool, optional): Whether to raise exceptions while fetching other details. Defaults to False.
    Example:
      parser = SearchResultParser(html_string, proxy="http://proxy.example.com", user_agent="CustomUserAgent/1.0", timeout=10)
      print(parser.anime)  # List of parsed anime details
      print(parser.episodes)  # List of parsed episode details
      print(parser.batch)  # List of parsed batch details
      #output
      #anime list
      [{'title': 'Anime Title', 'url': 'https://example.com/anime', 'thumbnails': {'width': '100', 'height': '100', 'url': 'https://example.com/thumbnail.jpg', 'srcset': ['https://example.com/thumbnail.jpg 1x', 'https://example
      .com/thumbnail.jpg 2x']}, 'genres': [{'text': 'Action', 'url': 'https://example.com/genre/action'}, {'text': 'Adventure', 'url': 'https://example.com/genre/adventure'}], 'status': 'Ongoing', 'rating': '8.0'}, ...]
#episode list
      [{'title': 'Episode 1', 'url': 'https://example.com/anime/episode/1', 'episode': '1'}, ...]
      #batch list
      [{'title': 'Batch Download', 'url': 'https://example.com/anime/batch'}, ...]
    """
  def __init__(self, html_string: str, **kwargs:dict):
    soup = bs(html_string, 'html.parser')
    self.anime = self.get_anime(soup)
    self.episodes = self.get_episodes(soup)
    self.batch = self.get_batch(soup)
    asyncio.run(AsyncParser.get_details(self, **kwargs))

  @staticmethod
  def get_anime(soup):
    pattern = animeSearchPattern
    elements = list(filter(lambda element: re.findall(pattern, element.a.text.lower()) if element.a else None, 
                 filter(lambda element: not element.get('class'), soup.find_all('li'))))
    return [
      {
        'title': element.a.text if element.a else None,
        'url': element.a.get('href') if element.a else None,
              'thumbnails': {
                'width': element.img.get('width'),
                'height': element.img.get('height'),
                'url': element.img.get('src'),
                'srcset': element.img.get('srcset').split()[::2] if element.img.get('srcset') and len(element.img.get('srcset').split()) > 1 else None,
                } if element.img else [],
                'genres': [
                  {
                    'text': genre.text,
                    'url': genre.get('href')
                    } for genre in element.div.find_all('a')] if element.div else [],
                'status': element.find_all('div')[1].text.split(':')[1].strip() if len(element.find_all('div')) > 1 and ':' in element.find_all('div')[1].text else None,
                'rating': element.find_all('div')[2].text.split(':')[1].strip() if len(element.find_all('div')) > 1 and ':' in element.find_all('div')[1].text else None,
                } for element in elements]

  @staticmethod
  def get_episodes(soup):
    pattern = episodeSearchPattern
    elements = list(filter(lambda element: re.findall(pattern, element.a.text.lower()) if element.a else None, 
                 filter(lambda element: not element.get('class'), soup.find_all('li'))))
    return [
      {
        'title': element.a.text,
        'url': element.a.get('href'),
        'episode': re.findall(pattern, element.a.text.lower())[0] if re.findall(pattern, element.a.text.lower()) else None}
        for element in elements
        if element.a]

  @staticmethod
  def get_batch(soup):
    elements = list(filter(lambda element: '[BATCH]' in element.a.text if element.a else None, filter(lambda element: not element.get('class'), soup.find_all('li'))))
    return [
      {'title': element.a.text,
       'url': element.a.get('href')
       }  for element in elements
       if element.a]

class AnimeParser(Parser):
  """
  AnimeParser is a class designed to parse anime-related data from a given URL (otakudesu anime page url). 
  It extracts various details such as title, description, episodes, seasons, and more 
  from the HTML content of the page using BeautifulSoup.
  Attributes:
    title (str): The title of the anime.
    details (dict): A dictionary containing detailed information about the anime.
    feed (list): A list of feeds related to the anime.
    description (str): A brief description of the anime.
    seasons (list): A list of seasons associated with the anime.
    episodes (list): A list of episodes of the anime.
    batch (dict): Batch download information for the anime.
  Methods:
    __init__(url: str, **kwargs: dict):
      Initializes the AnimeParser object by fetching and parsing the HTML content of the given URL.
        url (str): The URL of the otakudesu anime page to parse.
        **kwargs (dict): Optional keyword arguments:
          - user_agent (str): Custom User-Agent header for the HTTP request.
          - timeout (int): Timeout for the HTTP request (default is 10 seconds).
          - proxy (str): Proxy to use for the HTTP request.
    get_title(soup: bs4.BeautifulSoup) -> str:
      Extracts the title of the anime from the parsed HTML.
      args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object containing the parsed HTML.
      returns:
        str: The title of the anime, or None if not found.

    get_thumbnails(soup: bs4.BeautifulSoup) -> dict:
      Extracts thumbnail information from the parsed HTML.
      args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object containing the parsed HTML.
      returns:
        dict: A dictionary containing thumbnail details:
          - url (str): The URL of the thumbnail image.
          - width (str): The width of the thumbnail image.
          - height (str): The height of the thumbnail image.
          - srcset (list): A list of srcset URLs for the thumbnail image.

    get_details(soup: bs4.BeautifulSoup) -> dict:
      Extracts detailed information about the anime.
      args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object containing the parsed HTML.
      returns:
        dict: A dictionary containing anime details:
          - title (dict): A dictionary with 'title' and 'japanese' titles.
          - rating (str): The anime's rating.
          - producer (str): The producer of the anime.
          - type (str): The type of the anime (e.g., TV, Movie).
          - status (str): The current status of the anime (e.g., Ongoing, Completed).
          - totalEpisodes (str): The number of episodes.
          - duration (str): The duration of each episode.
          - releaseDate (str): The release date of the anime.
          - studio (str): The studio that produced the anime.
          - genres (list): A list of dictionaries with 'text' (genre name) and 'url' (genre page URL).

    get_feed(soup: bs4.BeautifulSoup) -> list:
      Extracts feed information related to the anime.
      args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object containing the parsed HTML.
      returns:
        list: A list of dictionaries containing feed details:
          - title (str): The title of the feed.
          - url (str): The URL of the feed.
          - thumbnail (str): The URL of the feed's thumbnail image.

    get_description(soup: bs4.BeautifulSoup) -> str:
      Extracts the description of the anime.
      args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object containing the parsed HTML.
        returns:
        str: The description of the anime, or an empty string if not found.

    get_seasons(soup: bs4.BeautifulSoup) -> list:
      Extracts season information associated with the anime.
      args:
      soup (bs4.BeautifulSoup): A BeautifulSoup object containing the parsed HTML.
      returns:
        list: A list of dictionaries containing season details:
          - title (str): The title of the season.
          - url (str): The URL of the season.

    get_episodes(soup: bs4.BeautifulSoup) -> list:
      Extracts episode information of the anime.
      args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object containing the parsed HTML.
        returns:
        list: A list of dictionaries containing episode details:
          - title (str): The title of the episode.
          - url (str): The URL of the episode.
          - releaseDate (str): The release date of the episode.

    get_batch(soup: bs4.BeautifulSoup) -> dict:
      Extracts batch download information for the anime.
      args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object containing the parsed HTML.
        returns:
        dict: A dictionary containing batch details:
          - title (str): The title of the batch.
          - url (str): The URL of the batch.
          - releaseDate (str): The release date of the batch.
  """
  def __init__(self, url: str, **kwargs: dict):
    response = httpx.get(
      url,
                            headers={'User-Agent': kwargs.get('user_agent', random.choice(userAgents))},
                            timeout=kwargs.get('timeout', 10),
                            proxy=kwargs.get('proxy')
                            )
    soup = bs(response.text, 'html.parser')
    self.title = self.get_title(soup)
    self.details = self.get_details(soup)
    self.feed = self.get_feed(soup)
    self.description = self.get_description(soup)
    self.seasons = self.get_seasons(soup)
    #self.linked_season = self.get_linked_season(soup) # This is not implemented in the parser
    self.episodes = self.get_episodes(soup) 
    self.batch = self.get_batch(soup)
    asyncio.run(AsyncParser.get_details(self, **kwargs))

  @staticmethod
  def get_title(soup: bs) -> str:
    return soup.div.h1.text if soup.div and soup.div.h1 else None

    @staticmethod
    def get_thumbnails(soup: bs) -> dict:
      element = soup.find('div', class_='fotoanime')
      return {
        'url': element.img.get('src') if element.img else None,
        'width': element.img.get('width') if element.img else None,
        'height': element.img.get('height') if element.img else None,
        'srcset': (element.img.get('srcset').split()[::2] if element.img.get('srcset') else None) if element.img else []
      }

  @staticmethod
  def get_details(soup: bs) ->dict:
    detailsSection = soup.find('div', class_='infozin').find_all('span') if soup.find('div', class_='infozin') else []
    details = {
      animeDetailsMapping.get(detail.text.split(detailsDelimiter, 2)[0].strip().lower(), detail.text.split(detailsDelimiter, 2)[0].strip().lower()): detail.text.split(detailsDelimiter, 2)[1].strip()
      for detail in detailsSection[:-1]
    if detail.text and detailsDelimiter in detail.text} if detailsSection else {}
    details['genres'] = [
      {
        'text': genre.text,
        'url': genre.get('href')
      }
    for genre in detailsSection[-1].find_all('a')] if detailsSection else []
    return details

  @staticmethod
  def get_feed(soup: bs) -> list:
    feeds = soup.find_all('div', class_='isi-anime')
    return [
    {
      'title': feed.text,
      'url': feed.a.get('href') if feed.a else None,
      'thumbnail': (feed.a.img.get('src') if feed.a.img else None) if feed.a else None
    }
    for feed in feeds]

  @staticmethod
  def get_description(soup: bs) -> str:
    return soup.find('div', class_='sinopc').text if soup.find('div', class_='sinopc') else ''

  @staticmethod
  def get_seasons(soup: bs) -> list:
    return [
      {
        'title': season.text,
        'url': season.get('href')
      }
       for season in soup.find('div', class_='sinopc').find_all('p')[1].find_all('a')
      ] if (element := soup.find('div', class_='sinopc')) and len(element.find_all('p')) > 1 else []

  #@staticmethod
  #def get_linked_season(soup: bs)->str:
    #linkedSeason = soup.find('div',class_='sinopc').a if soup.find('div',class_='sinopc') else None
    #return {
      #'title': linkedSeason.text,
      #'url': linkedSeason.get('href')
    #} if linkedSeason else {}

  @staticmethod
  def get_episodes(soup: bs):
    episodes = soup.find_all('div', class_='episodelist')[1].find_all('li') if len(soup.find_all('div', class_='episodelist')) > 1 else []
    return [
      {
        'title': episode.span.text,
        'url': episode.span.a.get('href') if episode.span.a else None,
        'releaseDate': episode.find_all('span')[-1].text if len(episode.find_all('span')) > 1 else None
      }
    for episode in episodes
    if episode.span][::-1]

  @staticmethod
  def get_batch(soup: bs) -> list:
    spans = soup.find('div', class_='episodelist').find_all('span') if soup.find('div', class_='episodelist') else []
    return {
      'title': spans[0].text,
      'url': spans[1].a.get('href'),
      'releaseDate': spans[2].text
    } if len(spans) > 2 else {}



class BatchParser(Parser):
  """
  BatchParser is a class designed to parse batch-related data from a given URL (otakudesu batch page url). 
  It extracts information such as the title, thumbnails, description, and download links.
  Args:
    url (str): The URL of the webpage to parse.
    **kwargs (dict): Additional optional arguments:
      - user_agent (str): Custom User-Agent header for the HTTP request. Defaults to a random choice from `userAgents`.
      - timeout (int): Timeout for the HTTP request in seconds. Defaults to 10.
      - proxy (str): Proxy to use for the HTTP request. Defaults to None.
  Attributes:
    title (str): The title of the batch extracted from the webpage.
    thumbnails (dict): A dictionary containing thumbnail information:
      - url (str): The URL of the thumbnail image.
      - width (str): The width of the thumbnail image.
      - height (str): The height of the thumbnail image.
      - srcset (list): A list of URLs for different resolutions of the thumbnail.
    description (str): The description of the batch.
    links (dict): A dictionary of download links categorized by resolution. Each resolution contains a list of dictionaries:
      - host (str): The name of the hosting service.
      - url (str): The URL of the download link.
  Methods:

    get_title(soup: bs4.BeautifulSoup) -> str:
      Extracts the title of the batch from the BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object of the parsed HTML.
      Returns:
        str: The title of the batch.

    get_thumbnails(soup: bs4.BeautifulSoup) -> dict:
      Extracts thumbnail information from the BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object of the parsed HTML.
      Returns:
        dict: A dictionary containing thumbnail details.

    get_description(soup: bs4.BeautifulSoup) -> str:
      Extracts the description of the batch from the BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object of the parsed HTML.
      Returns:
        str: The description of the batch.

    get_links(soup: bs4.BeautifulSoup) -> dict:
      Extracts download links categorized by resolution from the BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object of the parsed HTML.
      Returns:
        dict: A dictionary of download links categorized by resolution.
        each resolution contains a list of dictionaries:
          - host (str): The name of the hosting service.
          - url (str): The URL of the download link.

        example of usage:
        from OtaKuDesuData.parser import BatchParser
        url = 'https://otakudesu.cloud/batch/one-piece-batch-subtitle-indonesia/'
        parser = BatchParser(url)
        print(parser.title)
        print(parser.thumbnails)
        print(parser.description)
        print(parser.links)
        #output
        #One Piece Batch Subtitle Indonesia
        #{
        #  'url': 'https://example.com/thumbnail.jpg',
        #  'width': '100',
        #  'height': '100',
        #  'srcset': ['https://example
        #  .com/thumbnail.jpg 1x', 'https://example.com/thumbnail.jpg 2x']
        #}
        #Description of the batch
        #{'mp4480p': [{'host': 'Google Drive', 'url': 'https://example.com/download'}, ...], 'mp4720p': [{'host': 'Google Drive', 'url': 'https://example.com/download'}, ...], ...}

  """
  def __init__(self, url: str, **kwargs: dict):
    response = httpx.get(url,
                         headers={'User-Agent': kwargs.get('user_agent', random.choice(userAgents))},
                         timeout=kwargs.get('timeout', 10),
                         proxy=kwargs.get('proxy'))
    soup = bs(response.text, 'html.parser')
    self.title = self.get_title(soup)
    self.description = self.get_description(soup)
    self.thumbnails = self.get_thumbnails(soup)
    self.links = self.get_links(soup)
    asyncio.run(AsyncParser.get_details(self, **kwargs))

  @staticmethod
  def get_title(soup: bs) ->str:
    return soup.h4.text if soup.h4 else ''

  @staticmethod
  def get_description(soup: bs) ->str:
    return (soup.find('div',class_='deskripsi').p.text if soup.find('div',class_='deskripsi').p else '') if soup.find('div',class_='deskripsi') else ''

  @staticmethod
  def get_thumbnails(soup: bs)-> dict:
    element = soup.find('div',class_='animeinfo').img if soup.find('div',class_='animeinfo') else None
    if not element: return {}
    return {
      'url': element.get('src'),
      'width': element.get('width'),
      'height': element.get('height'),
      'srcset': element.get('srcset').split()[::2] if element.get('srcset') else []
    }

  @staticmethod
  def get_links(soup: bs) -> dict:
    batchResolutions = soup.find('div', class_='download2').find_all('li') if soup.find('div', class_='download2') else []
    links = {}
    for resolution in batchResolutions:
      links[resolution.strong.text.strip().lower()] = [
        {
          'host': link.text.strip().lower() if link.text else '',
          'url': link.get('href')
        }
        for link in resolution.find_all('a')
      ]
    return links

class EpisodeParser(Parser):
  """
  EpisodeParser is a class designed to parse episode-related data from a given URL (otakudesu episode page url). 
  It extracts information such as the title, thumbnails, details, episodes, and download links.
  Args:
    url (str): The URL of the webpage to parse.
    **kwargs (dict): Additional optional arguments:
      - user_agent (str): Custom User-Agent header for the HTTP request. Defaults to a random choice from `userAgents`.
      - timeout (int): Timeout for the HTTP request in seconds. Defaults to 10.
      - proxy (str): Proxy to use for the HTTP request. Defaults to None.
      - get_episode_details (bool): Whether to fetch detailed information for each episode. Defaults to False.
      raise_exception (bool): Whether to raise exceptions while fetching each episode  details. Defaults to False.
  Attributes:
    title (str): The title of the episode extracted from the webpage.
    thumbnails (dict): A dictionary containing thumbnail information:
      - url (str): The URL of the thumbnail image.
      - width (str): The width of the thumbnail image.
      - height (str): The height of the thumbnail image.
      - srcset (list): A list of URLs for different resolutions of the thumbnail.
    details (dict): A dictionary containing episode details such as:
      - uploader (str): The uploader of the episode.
      - uploadTime (str): The upload time of the episode.
      - genres (list): A list of genres, each represented as a dictionary with 'text' and 'url'.
      - Other details extracted based on the `episodeDetailsMapping`.
    episodes (list): A list of dictionaries representing episodes, each containing:
      - title (str): The title of the episode.
      - url (str): The URL of the episode.
    links (dict): A dictionary of download links categorized by resolution. Each resolution contains a list of dictionaries:
      - host (str): The name of the hosting service.
      - url (str): The URL of the download link.
  Methods:

    get_title(soup: bs4.BeautifulSoup) -> str:
      Extracts the title of the episode from the BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object of the parsed HTML.
      Returns:
        str: The title of the episode.

    get_thumbnails(soup: bs4.BeautifulSoup) -> dict:
      Extracts thumbnail information from the BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object of the parsed HTML.
      Returns:
        dict: A dictionary containing thumbnail details.

    get_details(soup: bs4.BeautifulSoup) -> dict:
      Extracts detailed information about the episode from the BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object of the parsed HTML.
      Returns:
        dict: A dictionary containing episode details.

    get_episodes(soup: bs4.BeautifulSoup) -> list:
      Extracts a list of episodes from the BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object of the parsed HTML.
      Returns:
        list: A list of dictionaries, each containing episode title and URL.

    get_links(soup: bs4.BeautifulSoup) -> dict:
      Extracts download links categorized by resolution from the BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object of the parsed HTML.
      Returns:
        dict: A dictionary of download links categorized by resolution.

        example of usage:
        from OtaKuDesuData.parser import EpisodeParser
        url = 'https://otakudesu.cloud/episode/one-piece-episode-1000/'
        parser = EpisodeParser(url)
        print(parser.title)
        print(parser.thumbnails)
        print(parser.details)
        print(parser.episodes)
        print(parser.links)
        #output
        #One Piece Episode 1000
        #{
        #  'url': 'https://example.com/thumbnail.jpg',
        #  'width': '100',
        #  'height': '100',
        #  'srcset': ['https://example
        #  .com/thumbnail.jpg 1x', 'https://example.com/thumbnail.jpg 2x']
        #}
        #{'uploader': 'Uploader Name', 'uploadTime': 'Upload Time', 'genres': [{'text': 'Action', 'url': 'https://otakudesu.cloud/genre/action'}, ...], ...}
        #[{'title': 'Episode 1', 'url': 'https://example.com/episode/1'}, ...]
        #{'mp4480p': [{'host': 'Google Drive', 'url': 'https://example.com/download'}, ...], 'mp4720p': [{'host': 'Google Drive', 'url': 'https://example.com/download'}, ...], ...}
  """
  def __init__(self, url: str, **kwargs: dict):
    response = httpx.get(url,
                         headers={'User-Agent': kwargs.get('user_agent', random.choice(userAgents))},
                         timeout=kwargs.get('timeout', 10),
                          proxy=kwargs.get('proxy'))
    soup = bs(response.text, 'html.parser')
    self.title = self.get_title(soup)
    self.thumbnails = self.get_thumbnails(soup)
    self.details = self.get_details(soup)
    self.episodes = self.get_episodes(soup)
    self.links = self.get_links(soup)
    asyncio.run(AsyncParser.get_details(self, **kwargs))

  @staticmethod
  def get_title(soup: bs) ->str:
    return soup.h4.text if soup.h4 else ''

  @staticmethod
  def get_thumbnails(soup: bs)->dict:
    element = soup.find('div',class_='cukder').img if soup.find('div',class_='cukder') else None
    if not element: return {}
    return {
      'url': element.get('src'),
      'width': element.get('width'),
      'height': element.get('height'),
      'srcset': element.get('srcset').split()[::2] if element.get('srcset') else []
    }

  @staticmethod
  def get_details(soup: bs)->dict:
    detailsSection = soup.find('div',class_='infozingle')
    if not detailsSection: return {}
    uploader = soup.find('div',class_='kategoz').find_all('span')[0].text.split('by', 2)[-1].strip() if soup.find('div',class_='kategoz') and len(soup.find('div',class_='kategoz').find_all('span')) > 1 else None
    uploadTime = soup.find('div',class_='kategoz').find_all('span')[1].text.split('on', 2)[-1].strip() if soup.find('div',class_='kategoz') and len(soup.find('div',class_='kategoz').find_all('span')) > 1 else None
    genres = [
        {
          'text': genre.text,
          'url': genre.get('href')
        }
        for genre in detailsSection.find_all('a')
      ]
    details = {
      episodeDetailsMapping.get(detail.text.split(detailsDelimiter, 2)[0].strip().lower(), detail.text.split(detailsDelimiter, 2)[0].strip().lower()): detail.text.split(detailsDelimiter, 2)[-1].strip()
    for detail in detailsSection.find_all('span') if detail.text and detailsDelimiter in detail.text}
    (details.update({'uploader': uploader}), details.update({'uploadTime': uploadTime}), details.update({'genres': genres}))
    return details

  @staticmethod
  def get_episodes(soup: bs)-> list:
    episodes = soup.find('div',class_='cukder').find_all('li') if soup.find('div',class_='cukder') else []
    return [
      {
        'title': episode.a.text if episode.a else None,
        'url': episode.a.get('href') if episode.a else None,
      }
    for episode in episodes][::-1]

  @staticmethod
  def get_links(soup: bs) -> dict:
    resolutions = soup.find('div', class_='download').find_all('li') if soup.find('div', class_='download') else []
    links = {}
    for resolution in resolutions:
      links[resolution.strong.text.strip().lower()] = [
        {
          'host': link.text.strip().lower() if link.text else '',
          'url': link.get('href')
        }
        for link in resolution.find_all('a')
      ]
    return links


class OngoingParser(Parser):
  """
  OngoingParser is a class designed to parse ongoing anime releases from a given URL (otakudesu ongoing anime url). 
  It supports caching for efficient navigation between pages and provides methods to 
  retrieve details about releases, navigate between pages, and extract metadata.

  Attributes:
    _cache (dict): A dictionary to store cached releases for each page.
    _previous_page_cache (dict): A dictionary to store cached previous page URLs for each page.
    _next_page_cache (dict): A dictionary to store cached next page URLs for each page.
    current_page (int): The current page number being parsed.
    previous_page (str): The URL of the previous page.
    next_page (str): The URL of the next page.
    releases (list): A list of parsed release details from the current page.
    use_cache (bool): A flag to enable or disable caching.
    _kwargs (dict): Additional keyword arguments passed during initialization.

  Methods:
    __init__(url: str, use_cache: bool = False, **kwargs: dict):
      Initializes the parser with the given URL and optional caching.
      Args:
        url (str): The URL of the page to parse.
        use_cache (bool, optional): Whether to enable caching. Defaults to False.
        **kwargs (dict): Additional options:
          - user_agent (str, optional): Custom User-Agent header. Defaults to a random choice from `userAgents`.
          - timeout (int, optional): Timeout for HTTP requests. Defaults to 10 seconds.
          - proxy (str, optional): Proxy to use for HTTP requests. Defaults to None.

    __iter__():
      Returns an iterator for the releases on the current page.

    __next__():
      Returns the next release in the iterator. If the end of the current page is reached, 
      it navigates to the next page (if available) and continues.

    results:
      Returns all releases across cached pages if caching is enabled, otherwise returns releases from the current page.

    previous():
      Navigates to the previous page and updates the parser state. Uses cache if enabled.

    next():
      Navigates to the next page and updates the parser state. Uses cache if enabled.

    get_releases(soup: bs4.BeautifulSoup) -> list:
      Extracts release details from the given BeautifulSoup object.
      Args:
        soup (bs): A BeautifulSoup object representing the parsed HTML.
      Returns:
        list: A list of dictionaries containing release details.

    get_all_pages(soup: bs4.BeautifulSoup) -> list:
      Extracts all page numbers and their URLs from the given BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object representing the parsed HTML.
      Returns:
        list: A list of dictionaries containing page numbers and URLs.

    get_previous_page(soup: bs4.BeautifulSoup) -> str:
      Extracts the URL of the previous page from the given BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object representing the parsed HTML.
      Returns:
        str: The URL of the previous page, or None if not available.

    get_next_page(soup: bs4.BeautifulSoup) -> str:
      Extracts the URL of the next page from the given BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object representing the parsed HTML.
      Returns:
        str: The URL of the next page, or None if not available.

    get_current_page_number(soup: bs4.BeautifulSoup) -> int:
      Extracts the current page number from the given BeautifulSoup object.
      Args:
        soup (bs4.BeautifulSoup): A BeautifulSoup object representing the parsed HTML.
      Returns:
        int: The current page number, or None if not available.

  Notes:
    - The `user_agent` keyword argument allows specifying a custom User-Agent header. If not provided, 
      a random User-Agent is selected from the `userAgents` list (from OtakuDesuData.constants).
    - The `timeout` keyword argument specifies the timeout for HTTP requests, with a default of 10 seconds.
    - The `proxy` keyword argument allows specifying a proxy for HTTP requests.
    - Methods like `get_anime_detail`, `get_episode_details`, and `get_batch_details` are not implemented 
      in this class but may be available in other classes like `SearchResultParser`.
  """
  _cache = {}
  _previous_page_cache = {}
  _next_page_cache = {}

  def __init__(self, url: str, use_cache: bool=False, **kwargs: dict):
    response = httpx.get(url,
                         headers={'User-Agent': kwargs.get('user_agent', random.choice(userAgents))},
                         timeout=kwargs.get('timeout', 10),
                          proxy=kwargs.get('proxy'))
    soup = bs(response.text, 'html.parser')
    self._kwargs = kwargs
    self.current_page = self.get_current_page_number(soup)
    self.previous_page = self.get_previous_page(soup)
    self.next_page = self.get_next_page(soup)
    self.releases = self.get_releases(soup)
    self.use_cache = use_cache
    if use_cache:
      self._cache[self.current_page] = self.releases
      self._previous_page_cache[self.current_page] = self.previous_page
      self._next_page_cache[self.current_page] = self.next_page


  def __iter__(self):
    self._current_index = 0
    return self

  def __next__(self):
    if self._current_index < len(self.releases):
      release = self.releases[self._current_index]
      self._current_index += 1
      return release
    elif self.next_page:
      self.next()
      self._current_index = 0
      return self.__next__()
    else:
      raise StopIteration

  @property
  def results(self):
    return [release for page in self._cache.values() for release in page] if self.use_cache else self.releases

  def previous(self):
    if self.previous_page:
      if current_page := (self.current_page - 1) in self._cache and self.use_cache:
        self.current_page = current_page
        self.next_page = self._next_page_cache[current_page]
        self.previous_page = self._previous_page_cache[current_page]
        self.releases = self._cache[current_page]
      else:
        response = httpx.get(self.next_page,
                             headers={'User-Agent': self._kwargs.get('user_agent', random.choice(userAgents))},
                             timeout=self._kwargs.get('timeout', 10),
                              proxy=self._kwargs.get('proxy'))
        soup = bs(response.text, 'html.parser')
        self.current_page = self.get_current_page_number(soup)
        self.next_page = self.get_next_page(soup)
        self.previous_page = self.get_previous_page(soup)
        self.releases = self.get_releases(soup)
        if self.use_cache:
          self._cache[self.current_page] = self.releases
          self._previous_page_cache[current_page] = self.get_previous_page(soup)
          self._next_page_cache[current_page] = self.get_next_page(soup)
    return self.releases

  def next(self):
    if self.next_page:
      if current_page := (self.current_page + 1) in self._cache and self.use_cache:
        self.current_page = current_page
        self.next_page = self._next_page_cache[current_page]
        self.previous_page = self._previous_page_cache[current_page]
        self.releases = self._cache[current_page]
      else:
        response = httpx.get(self.next_page,
                             headers={'User-Agent': self._kwargs.get('user_agent', random.choice(userAgents))},
                             timeout=self._kwargs.get('timeout', 10),
                              proxy=self._kwargs.get('proxy'))
        soup = bs(response.text, 'html.parser')
        self.current_page = self.get_current_page_number(soup)
        self.next_page = self.get_next_page(soup)
        self.releases = self.get_releases(soup)
        if self.use_cache:
          self._cache[self.current_page] = self.releases
          self._previous_page_cache[current_page] = self.get_previous_page(soup)
          self._next_page_cache[current_page] = self.get_next_page(soup)
    return self.releases

  @staticmethod
  def get_releases(soup: bs):
    releases = soup.find_all('div', class_='detpost')
    return [
      {
      'title': release.h2.text if release.h2 else None,
      'latestUpload': {
        'uploadDate': release.find(class_='newnime').text if release.find(class_='newnime') else None,
        'uploadDay': release.find('div', class_='epztipe').text if release.find('div', class_='epztipe') else None,
      'episode': release.find(class_='epz').text if release.find(class_='epz') else None
      },
      'url': release.a.get('href') if release.a else None,
      'thumbnail': {
        'url': release.img.get('src'),
        'width': release.img.get('width'),
        'height': release.img.get('height'),
        'srcset': release.img.get('srcset').split()[::2] if release.img.get('srcset') else []
      } if release.img else {}
      }
    for release in releases
    ]

  @staticmethod
  def get_all_pages(soup: bs)-> list:
    return [
      {
        'pageNumber': int(page.text) if page.text.isnumeric() else page.text,
        'url': page.get('href')
      }
     for page in soup.find_all('a',class_='page-numbers')]

  @staticmethod
  def get_previous_page(soup: bs) ->str:
    return soup.find('a', class_='prev page-numbers').get('href') if soup.find('a', class_='prev page-numbers') else None

  @staticmethod
  def get_next_page(soup: bs) ->str:
    return soup.find('a', class_='next page-numbers').get('href') if soup.find('a', class_='next page-numbers') else None

  @staticmethod
  def get_current_page_number(soup: bs) ->int:
    return (int(soup.find('span', class_='page-numbers current').text) if soup.find('span', class_='page-numbers current').text.isnumeric() else soup.find('span', class_='page-numbers current').text) if soup.find('span', class_='page-numbers current') else None

class AsyncParser(Parser):
  def __init__(self, client: httpx.AsyncClient, **kwargs: dict):
    self._client = client
    self._proxy = kwargs.get('proxy')
    self._userAgent = kwargs.get('user_agent')
    self._timeout = kwargs.get('timeout', 10)

  @staticmethod
  async def get_details(self, **kwargs: dict)-> None:
    try:
      async with httpx.AsyncClient(proxy=kwargs.get('proxy')) as client:
        parser = AsyncParser(
          client,
          timout=kwargs.get('timeout'),
          user_agent=kwargs.get('user_agent')
        )
        tasks = []
        tasks.extend( [asyncio.create_task(parser.asyncGetAnimeDetails(anime, update_details=kwargs.get('update_details'))) for anime in getattr(self, 'anime', []) ] if kwargs.get('get_anime_details') else [])
        tasks.extend( [asyncio.create_task(parser.asyncGetEpisodeDetails(episode)) for episode in getattr(self,'episodes',[]) ] if kwargs.get('get_episode_details') else [])
        tasks.extend( [asyncio.create_task(parser.asyncGetBatchDetails(batch)) for batch in getattr(self, 'batch',[]) ] if kwargs.get('get_batch_details') else [])
        await asyncio.gather(*tasks)
    except Exception as e:
      if kwargs.get('raise_exception'): raise e

  async def asyncGetAnimeDetails(self, anime: dict, update_details: bool=False)-> None:
    try:
      r = await self._client.get(
        url=anime['url'],
        headers={'User-Agent': self._userAgent or random.choice(userAgents)},
                           timeout=self._timeout
                           )
      soup = bs(r.text, 'html.parser')
      details = AnimeParser.get_details(soup)
      [anime.update({key: details.get(key)}) for key in details.keys() if key not in anime.keys() and not update_details]                        
      anime['episodes'] = AnimeParser.get_episodes(soup)
      anime['batch'] = AnimeParser.get_batch(soup)
      anime['description'] = AnimeParser.get_description(soup)
      anime['seasons'] = AnimeParser.get_seasons(soup)
      anime['feeds'] = AnimeParser.get_feed(soup)
    except Exception as e:
      raise e

  async def asyncGetEpisodeDetails(self, episode: dict)->None:
    try:
      r = await self._client.get(
        url=episode['url'],
        headers={'User-Agent': self._userAgent or random.choice(userAgents)},
                           timeout=self._timeout
                           )
      soup = bs(r.text, 'html.parser')
      episode['details'] = EpisodeParser.get_details(soup)
      episode['thumbnails'] = EpisodeParser.get_thumbnails(soup)
      episode['otherEpisodes'] = EpisodeParser.get_episodes(soup)
      episode['links'] = EpisodeParser.get_links(soup)
    except Exception as e:
      print(e)
      raise e

  async def asyncGetBatchDetails(self, batch:dict)-> None:
    try:
      r = await self._client.get(
        url=batch['url'],
        headers={'User-Agent': self._userAgent or random.choice(userAgents)},
                           timeout=self._timeout
                           )
      soup = bs(r.text, 'html.parser')
      batch['thumbnails'] = BatchParser.get_thumbnails(soup)
      batch['description'] = BatchParser.get_description(soup)
      batch['links'] = BatchParser.get_links(soup)
    except Exception as e:
      raise e
