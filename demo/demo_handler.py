# -*- coding: utf-8 -*-

import sys
import os
import time
import signal
import json
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
import tornado
from common import RESTfulHandler
from setting import LOGGER
RELATED_URL = 'https://www.baidu.com' 

class TestHandler(RESTfulHandler):
    Count = 0
    
    def __init__(self, *arg, **kargs):
        super(TestHandler, self).__init__(*arg, **kargs)
        # self.request.downstream_name 用于prometheus 监控; 标注下游服务。
        self.request.downstream_name = "demo"

    async def get(self, *arg, **kwargs ):
        LOGGER.info("pid: %d; res: test %d"% (os.getpid(), TestHandler.Count))
        res = await self.handle_get()
        # self.request.response 用于prometheus 监控; 用于监控下游返回状态。
        self.request.response = res
        self.finish(res.body)
        return

    async def handle_get(self):
        http_client = AsyncHTTPClient()
        url = RELATED_URL 
        response = await http_client.fetch(url)
        return response

    """
    async def handler_post(self):
        http_client = AsyncHTTPClient()
        url = RELATED_URL + self.uri
        # connect_timeout: Timeout for initial connection in seconds, default 20 seconds
        # request_timeout: Timeout for entire request in seconds, default 20 seconds
        # body : HTTP request body as a string (byte or unicode; if unicode the utf-8 encoding will be used)
        response = await http_client.fetch(url, method="POST")   # connect_timeout=; request_timeout=; body=;
        return response
    """

