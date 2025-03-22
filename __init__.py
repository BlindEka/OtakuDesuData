from OtakuDesuData.parser import SearchResultParser, Parser, OngoingParser
from OtakuDesuData.constants import *
from bs4 import BeautifulSoup as bs
import httpx
import random


class SearchTypes:
  anime = 'anime'
  batch = 'batch'
  episode = 'episode'


def search(query: str, search_type: SearchTypes=SearchTypes.anime, timeout=10, proxy=None, **kwargs):
  params = {'s': query, 'post_type': search_type}
  r = httpx.get(baseUrl, timeout=timeout, params=params, proxy=proxy, headers={'User-Agent': kwargs.get('user_agent', random.choice(userAgents))})
  results = SearchResultParser(r.text, timeout=timeout, proxy=proxy, **kwargs)
  return results.results

def get_ongoing(get_all: bool=False):
  ongoing = OngoingParser(ongoingUrl)
  if not get_all:
    return ongoing
  results = []
  for i in ongoing:
    results.append(i)
  return results

def get_schedules(**kwargs: dict):
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
  response = httpx.get(animeListUrl,
                       headers={'User-Agent': kwargs.get('user_agent', random.choice(userAgents))},
                       timeout=kwargs.get('timeout', 10),
                        proxy=kwargs.get('proxy'))
  soup = bs(response.text,'html.parser')
  animeListElements = list = soup.find_all('a',class_='hodebgst')
  return [
    {
      'title': animeListElement.text.strip() if animeListElement.text else None,
      'url': animeListElement.get('href')
    }
  for animeListElement in animeListElements]
