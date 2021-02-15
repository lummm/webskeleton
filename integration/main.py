#!/usr/bin/env python3.9

import asyncio
from concurrent.futures import Future
from queue import Queue
import os
import threading
import time

import pytest
from webskeleton import WebSkeleton

import controllers


def run_server(q: Queue):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async def run():
        print("running server...")
        app = WebSkeleton(controllers)
        server_task = loop.create_task(app.run_async())
    loop.create_task(run())
    loop.run_forever()
    return


def run_tests():
    time.sleep(1)               # let the server start
    print("running tests")
    tests = [f for f in os.listdir("./test")
             if "_test" in f]
    pytest.main(tests)
    return


def main():
    q = Queue()
    server = threading.Thread(
        target=lambda: run_server(q), daemon=True
    )
    server.start()
    run_tests()
    return


if __name__ == '__main__':
    main()
