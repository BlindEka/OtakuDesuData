import requests
import asyncio
import httpx
from OtakuDesuData.constants import userAgents
import os
import random

class RequestCore:
  def __init__(self, client=None, proxy: dict={}, **kwargs):
    self.client = client
    self.timeout = kwargs.get('timeout', 10)
    self.userAgents = userAgents
    if not proxy:
      self.proxy = {}
      http_proxy = os.environ.get("HTTP_PROXY")
      if http_proxy:
        self.proxy["http://"] = http_proxy
      https_proxy = os.environ.get("HTTPS_PROXY")
      if https_proxy:
        self.proxy["https://"] = https_proxy

  @staticmethod
  async def get(self, url, **kwargs)-> httpx.Response:
    return requests.get(url=url, headers={'User-Agent': kwargs.get('user_agent', random.choice(self.userAgents))} if not kwargs.get('headers') else kwargs.get('headers'), timeout=kwargs.get('timeout', self.timeout))

  async def asyncGet(self, url, **kwargs)-> httpx.Response:
    try:
      return await self.client.get(
        url=url,
                        headers={'User-Agent': kwargs.get('user_agent', random.choice(self.userAgents))} if not kwargs.get('headers') else kwargs.get('headers'),
                        timeout=kwargs.get('timeout', self.timeout)
                        )
    except Exception as e:
      print(e)
      raise e
