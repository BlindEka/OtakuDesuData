import requests
import asyncio
import httpx
from OtakuDesuData.constants import userAgents
import os
import random

class RequestCore:
  def __init__(self, proxy=None, **kwargs):
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

    def syncGetRequest(self, url) -> httpx.Response:
        return httpx.get(url,
                         headers={"User-Agent": kwargs.get('user_agent', random.choice(self.userAgents))},
                         timeout=self.timeout,
                         cookies=kwargs.get('cookies'),
                         proxy=self.proxy)

  async def asyncGetRequest(self, url:str, **kwargs: dict) -> httpx.Response:
    async with httpx.AsyncClient(proxy=self.proxy) as client:
      return await client.get(
        url,
        headers={"User-Agent": kwargs.get('user_agent', random.choice(self.userAgents))},
        timeout=self.timeout,
        cookies=kwargs.get('cookies')
        )
