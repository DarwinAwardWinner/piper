import os
from setuptools import setup, find_packages

def read_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "piper",
    version = "0.1dev",
    packages = find_packages(),

    # metadata for upload to PyPI
    author = "Ryan C. Thompson",
    author_email = "rct@thompsonclan.org",
    description = "Easily set up shell pipelines in Python",
    license = "BSD",
    keywords = ("subprocess", "pipe", "pipeline"),
    #url = "http://example.com/HelloWorld/",   # project home page, if any
    long_description=read_file('README.md'),
)
