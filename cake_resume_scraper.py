import random
import re
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

class CakeResumeJobDescScraper:
    def __init__(self, title, n_pages):
        self._title = title
        self._n_pages = n_pages
    def get_first_n_page_job_links(self):
        request_url = "https://www.cakeresume.com/jobs"
        out_job_links = []
        out_job_titles = []
        out_companies = []
        for i in range(1, self._n_pages + 1):
            query_string_parameters = {
                'q': self._title,
                'refinementList[job_type][0]': 'full_time',
                'refinementList[seniority_level][0]': 'entry_level',
                'page': str(i)
            }
            response = requests.get(request_url, params=query_string_parameters)
            soup = BeautifulSoup(response.text, "lxml")
            job_links = [e.get('href') for e in soup.select('.job-link')]
            job_titles = [e.text for e in soup.select('.job-link')]
            companies = [e.text for e in soup.select(".page-name a")]
            out_job_links += job_links
            out_job_titles += job_titles
            out_companies += companies
            rand_int = random.randint(1, 3)
            print("Scraping page {}...".format(i))
            print("Sleeping for {} secs...".format(rand_int))
            time.sleep(rand_int)
        return out_job_links, out_job_titles, out_companies
    def get_job_descriptions(self):
        job_links, job_titles, companies = self.get_first_n_page_job_links()
        job_descriptions = []
        for job_link, job_title, company in zip(job_links, job_titles, companies):
            response = requests.get(job_link)
            soup = BeautifulSoup(response.text, "lxml")
            job_desc_str = ''
            for e in soup.select(".section"):
                job_desc_str += e.text
            job_descriptions.append(job_desc_str)
            rand_int = random.randint(1, 5)
            print("正在爬取{}的{}工作描述...".format(company, job_title))
            time.sleep(rand_int)
        out = pd.DataFrame()
        out["company"] = companies
        out["jobTitle"] = job_titles
        out["jobDesc"] = job_descriptions
        return out