from argparse import ArgumentParser
import sys
from indeed_mongodb_scrapper.scraping import IndeedScrapperMongo




def main():
    parser = ArgumentParser(add_help=True)
    parser.add_argument('--country', default="fr", type=str)
    parser.add_argument('--position', default="java devlopper", type=str)
    parser.add_argument('--location', default="Paris", type=str)
    parser.add_argument('--num_pages', default=10, type=int)
    parser.add_argument('--sleep_min', default=60, type=int)
    parser.add_argument('--sleep_max', default=120, type=int)
    parser.add_argument('--mongodb_db_name', default="jobs", type=str)
    parser.add_argument('--mongodb_colection_name', default="indeed", type=str)
    parser.add_argument('--mongo_host', default="localhost", type=str)
    parser.add_argument('--mongo_port', default=27017, type=int)


    args = parser.parse_args()

    scraper = IndeedScrapperMongo(**vars(args))

    scraper.scrape()

if __name__ == '__main__':
    args = sys.argv
    if "--help" in args or len(args) == 1:
        print("CVE")
    main()