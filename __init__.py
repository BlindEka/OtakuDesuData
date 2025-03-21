from OtakuDesuData.parser import SearchResultParser, Parser, OngoingParser
from OtakuDesuData.constants import baseUrl, userAgent, ongoingUrl, animeListUrl, schedulesUrl, dayMapping
from bs4 import BeautifulSoup as bs
import requests


class SearchTypes:
  anime = 'anime'
  batch = 'batch'
  episode = 'episode'


def search(query: str, search_type: SearchTypes=SearchTypes.anime, **kwargs):
  pass

class OtakuDesuSearch(Parser):
  def __init__(self, query:str, search_type: SearchTypes=None, timeout: int=10, user_agent: str=userAgent):
    params = {'s': query, } if not search_type else {'s': query, 'post_type': search_type}
    response = requests.get(url=baseUrl, params=params, headers={'User-Agent': user_agent}, timeout=timeout)
    response.raise_for_status()
    contents = SearchResultParser(response.content)
    self.anime = contents['anime']
    self.batch = contents['batch']
    self.episodes = contents['episodes']
    results = {
      'anime': contents.anime,
      'episodes': contents.episodes,
      'batch': contents.batch
    }
    self.results = results

def get_ongoing(get_all: bool=False):
  ongoing = OngoingParser(ongoingUrl)
  if not get_all:
    return ongoing
  results = []
  for i in ongoing:
    results.append(i)
  return results

def get_schedules():
  response = requests.get(schedulesUrl, headers={'User-Agent': userAgent})
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

def get_anime_list():
  response = requests.get(animeListUrl, headers={'User-Agent': userAgent})
  soup = bs(response.text,'html.parser')
  animeListElements = list = soup.find_all('a',class_='hodebgst')
  return [
    {
      'title': animeListElement.text.strip() if animeListElement.text else None,
      'url': animeListElement.get('href')
    }
  for animeListElement in animeListElements]
