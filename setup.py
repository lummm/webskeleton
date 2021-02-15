#!/usr/bin/env python

from setuptools import find_packages, setup


setup(name='webskeleton',
      version='v0.1.0',
      description='Web skeleton',
      author='Liam Tengelis',
      author_email='liam@tengelisconsulting.com',
      url='https://github.com/tengelisconsulting/webskeleton',
      download_url='https://github.com/tengelisconsulting/webskeleton/archive/v0.1.0.tar.gz',
      install_requires=[
          "aiohttp==3.7.3",
          "aioredis==1.3.1",
          "asyncpg==0.21.0",
          "multidict==5.1.0",
          "PyJWT==2.0.0",
          "PyPika==0.46.0",
          "python-box==5.2.0",
          "uvloop==0.14.0",
          "yarl==1.6.3",
      ],
      packages=find_packages(),
      package_data={
          '': ['*.yaml'],
          "webskeleton": ["py.typed"],
      },
)
