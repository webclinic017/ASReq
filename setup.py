from setuptools import setup

from os import path

curdir = path.abspath(path.dirname(__file__))  # the directory where the file is located
readme_fp = path.join(curdir, "README.md")  # the path where the README is located
require_fp = path.join(curdir, "requirements.txt")  # the path where the requirements are located

with open(readme_fp, "r") as f:  # read the readme and put it into the long description for later
    long_desc = f.read()

with open(require_fp, "r") as f:  # read and split the requirements in requirements.txt
    require = f.read().split("\n")

setup(
    name='gachi_http',
    version='0.1.2',
    packages=['gachi_http'],
    # pip doesn't recognize requirements.txt afaik
    install_requires=require,
    # type annotations were introduced in 3.8, and since major versions break backwards compatibility, we go the safe route of disallowing 4.x
    python_requires=">=3.6, <4",
    # adding the README to pypi
    long_description=long_desc,
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/gachi-http',
    license='GPL3',
    author='xazkerboy & edman',
    author_email='admin@quot.pw',
    description='Add-on over aiohttp for more convenience'
)
