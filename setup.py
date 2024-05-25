#!/usr/bin/env python

from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(name='rxd',
      version='0.0.1',
      description='A reactive application manager',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Huy Nguyen',
      author_email='121183+huyng@users.noreply.github.com',
      packages=['rxd'],
      install_requires=["Flask"],
      zip_safe=False,
      url="https://github.com/huyng/rxd")

# to distribute run:
# python setup.py register sdist upload
# python -m twine  upload dist
