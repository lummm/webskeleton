#!/usr/bin/env python3

import asyncio
import os

from webskeleton import WebSkeleton

import demo_controllers


def main():
    app = WebSkeleton(demo_controllers)
    app.run(
        port=8000,
        dbhost=os.environ["PGHOST"],
        dbpassword=os.environ["PGPASSWORD"],
    )
    return


if __name__ == '__main__':
    main()
