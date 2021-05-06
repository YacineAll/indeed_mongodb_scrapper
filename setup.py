from setuptools import find_packages, setup
from io import open
from os import path

import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent


README = (HERE / "README.md").read_text()


with open(path.join(HERE, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if ('git+' not in x) and ( not x.startswith('#')) and (not x.startswith('-')) and (not len(x)==0)]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs  if 'git+' not in x]


setup(
    name='indeed_mongodb_scrapper',
    version='0.1.0',
    description='Indeed Scrapper storing the data on MongoDB database',
    author='Yacine ALLOUACHE',
    author_email='oyetoketoby80@gmail.com',
    license='MIT',
    keyword="scrapping, indeed, jobs, mongodb",
    url='https://github.com/YacineAll/indeed_mongodb_scrapper',
    download_url='https://github.com/YacineAll/indeed_mongodb_scrapper/archive/refs/tags/0.1.0.tar.gz',
    entry_points='''
        [console_scripts]
        indeed_mongodb_scrapper=indeed_mongodb_scrapper.__main__:main
    ''',
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=install_requires,
    dependency_links=dependency_links,
    setup_requires=['pytest-runner==5.3.0'],
    tests_require=['pytest==6.2.3'],
    test_suite='tests',
    python_requires='>=3.8',
)