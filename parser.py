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
    def get_details(soup: bs) -> dict:
      """
      Extracts anime details from a BeautifulSoup object.

      Args:
        soup (bs): A BeautifulSoup object containing the parsed HTML of the anime page.

      Returns:
        dict: A dictionary containing the extracted anime details:
          - title: A dictionary with 'title' (str) and 'japanese' (str) titles.
          - rating: The anime's rating (str).
          - producer: The producer of the anime (str).
          - type: The type of the anime (e.g., TV, Movie) (str).
          - status: The current status of the anime (e.g., Ongoing, Completed) (str).
          - totalEpisodes: The number of episodes (str).
          - duration: The duration of each episode (str).
          - releaseDate: The release date of the anime (str).
          - studio: The studio that produced the anime (str).
          - genres: A list of dictionaries, each containing:
            - 'text': The genre name (str).
            - 'url': The URL to the genre page (str).
      """
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
