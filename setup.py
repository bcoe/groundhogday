#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(name="groundhogday",
      version="0.0.3",
      description="GroundhogDay lets you repeat an operation until you get it right.",
      author="Benjamin Coe",
      author_email="ben@attachments.me",
      entry_points = {},
      url="https://github.com/bcoe/groundhogday",
      packages = find_packages(),
      install_requires = ['Pytoad==1.0.7'],
      tests_require=['nose']
)
