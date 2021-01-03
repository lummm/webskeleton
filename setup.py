#!/usr/bin/env python

from setuptools import find_packages, setup


setup(name='webskeleton',
      version='v0.1.0',
      description='Web skeleton',
      author='Liam Tengelis',
      author_email='liam@tengelisconsulting.com',
      url='https://github.com/tengelisconsulting/webskeleton',
      # download_url=("https://github.com"
      #               "/tengelisconsulting/ez_arch_worker"
      #               "/archive/v0.3.87.tar.gz"),
      packages=find_packages(),
      package_data={
          '': ['*.yaml'],
      },
)
