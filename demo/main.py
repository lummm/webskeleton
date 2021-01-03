#!/usr/bin/env python3

from webskeleton import load_routes

import demo_controllers


def main():
    app = load_routes(demo_controllers)
    app.run(8888)
    return


if __name__ == '__main__':
    main()
