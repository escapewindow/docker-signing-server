#!/usr/bin/env python
""" Test the ssl_test_server.  Requires python3.5 with requests and aiohttp
This will throw an exception if the test fails.
"""
from __future__ import print_function

import aiohttp
import asyncio
import os
import requests
import ssl

URL = "https://localhost:8080/?foo=bar"
SSL_CERT = os.path.join(
    os.path.dirname(__file__),
    "..",
    "fake_ca", "ca.crt"
)
ssl_context = ssl.create_default_context(cafile=SSL_CERT)

def req():
    resp = requests.get(URL, verify=SSL_CERT)

async def aio():
    aio_conn = aiohttp.TCPConnector(ssl_context=ssl_context)
    with aiohttp.ClientSession(connector=aio_conn) as session:
        resp = await session.get(URL)
        resp.close()

req()
loop = asyncio.get_event_loop()
loop.run_until_complete(aio())
loop.close()
