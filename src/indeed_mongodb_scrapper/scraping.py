import requests
import random
import pymongo
from time import sleep
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
from typing import Iterable


class IndeedScrapperMongo:
    """IndeedScrapperMongo is a job scraper for Indeed storing the data on MongoDB"""

    def __init__(self, country: str, position: str, location: str, num_pages: int = 10,  sleep_min: int = 30, sleep_max: int = 60, mongodb_db_name: str = 'jobs',  mongodb_colection_name: str = 'indeed', mongo_host: str = 'localhost', mongo_port: int = 27017, *args, **kwargs):
        """
        Create a JobsScraper object

        Args:
            country (str): country prefix.
                            Available countries:
                                AE, AQ, AR, AT, AU, BE, BH, BR, CA, CH, CL, CO,
                                CZ, DE, DK, ES, FI, FR, GB, GR, HK, HU, ID, IE,
                                IL, IN, IT, KW, LU, MX, MY, NL, NO, NZ, OM, PE,
                                PH, PK, PL, PT, QA, RO, RU, SA, SE, SG, TR, TW,
                                US, VE, ZA.

            position (str): Job position eg: 'technologies'

            location (str): Job location eg:'france'

            num_pages (int, optional): Number of pages to be scraped. Each page contains 15 results. Defaults to 10.

            sleep_min (int, optional): min delay to sleep. Defaults to 30 seconds.

            sleep_max (int, optional): max delay to sleep. Defaults to 60 seconds.

            mongodb_db_name (str, optional): Name of the database where the data will be stored. Defaults to 'jobs'.

            mongodb_colection_name (str, optional): Name of the collection where the data will be stored. Defaults to 'indeed'.

            mongo_host (str, optional): MongoDB hostname or IP address. Defaults to 'localhost'.

            mongo_port (int, optional): MongoDB port. Defaults to 27017.
        """

        self.__num_pages = num_pages

        self.__country = country

        self.__mongodb_db_name = mongodb_db_name
        self.__mongodb_colection_name = mongodb_colection_name

        self.__sleep_max = sleep_max
        self.__sleep_min = sleep_min
        self.__mongo_host = mongo_host
        self.__mongo_port = mongo_port

        if country.upper() == "US":
            self.__url = 'https://indeed.com/jobs?q={}&l={}'.format(
                position, location)
        else:
            self.__url = 'https://{}.indeed.com/jobs?q={}&l={}'.format(
                country, position, location)
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}

        myclient = pymongo.MongoClient(
            host=self.__mongo_host,
            port=self.__mongo_port,
            document_class=dict,
            tz_aware=False,
            connect=True
        )

        mydb = myclient[self.__mongodb_db_name]
        self.__mongo_col = mydb[self.__mongodb_colection_name]

        self.__count = 0

    def get_data(self) -> Iterable:
        """This function gets all the documents stored in the MongoDB database in the form list of dictionaries and each dictionary contains these keys:
            {
                "_id": str,
                "title": str,
                "location": str,
                "company": str,
                "summary": str,
                "job_description": str,
            }

        Returns:
            Iterable: list of dictionaries.
        """

        myclient = pymongo.MongoClient(
            host=self.__mongo_host,
            port=self.__mongo_port,
            document_class=dict,
            tz_aware=False,
            connect=True
        )

        mydb = myclient[self.__mongodb_db_name]
        mongo_col = mydb[self.__mongodb_colection_name]

        result = [doc for doc in mongo_col.find()]

        return result

    def __extract_page(self, page):

        with requests.Session() as request:
            r = request.get(url="{}&start={}".format(
                self.__url, page), headers=self.__headers)

        soup = BeautifulSoup(r.content, 'html.parser')

        return soup

    def __transform_and_save_page(self, soup, page):

        jobs = soup.find_all('div', class_='jobsearch-SerpJobCard')

        for job in jobs:

            try:
                title = job.find(
                    'a', class_='jobtitle').text.strip().replace('\n', '')
            except:
                title = None
            try:
                company = job.find(
                    'span', class_='company').text.strip().replace('\n', '')
            except:
                company = None
            try:
                summary = job.find(
                    'div', {'class': 'summary'}).text.strip().replace('\n', '')
            except:
                summary = None

            if job.find('div', class_='location'):
                try:
                    location = job.find(
                        'div', class_='location').text.strip().replace('\n', '')
                except:
                    location = None
            else:
                try:
                    location = job.find(
                        'span', class_='location').text.strip().replace('\n', '')
                except:
                    location = None
            try:
                href = job.h2.a.get('href')
                if self.__country.upper() == "US":
                    job_url = 'https://indeed.com{}'.format(href)
                else:
                    job_url = 'https://{}.indeed.com{}'.format(
                        self.__country, href)
            except:
                job_url = None

            try:
                url = f"{job_url}&start={0}"
                with requests.Session() as request:
                    r = request.get(url=url, headers=self.__headers)

                job_description = BeautifulSoup(r.content, 'html.parser')
                job_description = job_description.find(
                    "div", {"id": "jobDescriptionText"})
                job_description = '\n\n'.join(
                    [i.text for i in job_description.children])
            except:
                job_description = None

            try:
                salary = job.find(
                    'span', class_='salary').text.strip().replace('\n', '')
            except:
                salary = None

            job = {
                'title': title,
                'location': location,
                'company': company,
                'summary': summary,
                'job_description': job_description,
                'salary': salary,
                'url': job_url
            }

            self.__count += 1
            self.__mongo_col.insert_one(job)

            print("Scraping job N°:{}, page: {}, title: {}...".format(
                self.__count, page, title))
            sleep(random.randint(self.__sleep_min, self.__sleep_max))

    def scrape(self) -> None:
        """Scraping data and store them in MongoDB database. This function will create `jobs` database on MongoDB and indeed collection in this `jobs` database.
        """
        for i in tqdm(range(0, self.__num_pages * 10, 10), desc="Scraping in progress...", total=self.__num_pages):
            page = self.__extract_page(i)
            self.__transform_and_save_page(page, i)
