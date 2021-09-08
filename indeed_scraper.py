import random
import re
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

class IndeedJobDescScraper:
    def __init__(self, title, n_pages):
        self._title = title
        self._n_pages = n_pages
    def get_first_n_page_job_keys(self):
        request_url = "https://tw.indeed.com/jobs"
        out = []
        for i in range(0, self._n_pages * 10, 10):
            query_string_parameters = {
                'q': self._title,
                'jt': 'fulltime',
                'start': str(i)
            }
            response = requests.get(request_url, params=query_string_parameters)
            soup = BeautifulSoup(response.text, "lxml")
            job_keys = [e.get('data-jk') for e in soup.select('#mosaic-provider-jobcards a')]
            job_keys = [jk for jk in job_keys if jk is not None]
            out += job_keys
            rand_int = random.randint(1, 3)
            print("Scraping page {}...".format(i // 10 + 1))
            time.sleep(rand_int)
        return out
    def get_job_descriptions(self):
        first_n_page_job_keys = self.get_first_n_page_job_keys()
        companies = []
        job_titles = []
        job_descriptions = []
        for job_key in first_n_page_job_keys:
            query_string_paramters = {
                'jk': job_key
            }
            request_url = 'https://tw.indeed.com/viewjob'
            response = requests.get(request_url, params=query_string_paramters)
            soup = BeautifulSoup(response.text, "lxml")
            job_title = [e.text for e in soup.select("h1")][0]
            company = [e.text for e in soup.select(".icl-u-lg-mr--sm")][0]
            jd = [e.text for e in soup.select("#jobDescriptionText")][0]
            companies.append(company)
            job_titles.append(job_title)
            job_descriptions.append(jd)
            rand_int = random.randint(1, 3)
            print("正在爬取{}的{}工作描述...".format(company, job_title))
            time.sleep(rand_int)
        out = pd.DataFrame()
        out["company"] = companies
        out["jobTitle"] = job_titles
        out["jobDesc"] = job_descriptions
        out.insert(0, "jdSource", "Indeed")
        return out