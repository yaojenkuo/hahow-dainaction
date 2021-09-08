import random
import re
import time
import requests
import pandas as pd

class OneOFourJobDescScraper:
    def __init__(self, title):
        self._title = title
    def get_n_pages(self):
        request_url = "https://www.104.com.tw/jobs/search/list"
        request_headers = {
            'Referer': 'https://www.104.com.tw/jobs/search/'
        }
        query_string_parameters = {
            'ro': '1',
            'kwop': '7',
            'keyword': self._title,
            'jobcatExpansionType': 'area,spec,com,job,wf,wktm',
            'order': '15',
            'asc': '0',
            'page': '1',
            'mode': 's',
        }
        response = requests.get(request_url, params=query_string_parameters, headers=request_headers)
        response_json = response.json()
        n_jobs = response_json['data']['totalCount']
        n_pages = response_json['data']['totalPage']
        print("符合搜尋條件的職缺有{}筆，分佈在{}頁".format(n_jobs, n_pages))
        return n_pages
    def get_job_links(self, n_pages=5):
        job_links = []
        request_headers = {
            'Referer': 'https://www.104.com.tw/jobs/search/'
        }
        for page in range(1, n_pages + 1):
            query_string_parameters = {
                'ro': '1',
                'kwop': '7',
                'keyword': self._title,
                'jobcatExpansionType': 'area,spec,com,job,wf,wktm',
                'order': '15',
                'asc': '0',
                'page': str(page),
                'mode': 's',
            }
            request_url = "https://www.104.com.tw/jobs/search/list"
            response = requests.get(request_url, params=query_string_parameters, headers=request_headers)
            response_json = response.json()
            for job in response_json['data']['list']:
                job_link = job['link']['job'].replace('//', '')
                job_link = "https://{}".format(job_link)
                job_links.append(job_link)
            print("正在爬取第{}頁的職缺...".format(page))
            sleep_time = random.randint(5, 10)
            time.sleep(sleep_time)
        return job_links
    def get_job_descriptions(self):
        job_links = self.get_job_links()
        job_ids = [re.split("/|\?", i)[-2] for i in job_links]
        job_descriptions = []
        request_headers = {
            'Referer': 'https://www.104.com.tw/jobs/search/'
        }
        for job_id, job_link in zip(job_ids, job_links):
            request_url = "https://www.104.com.tw/job/ajax/content/{}".format(job_id)
            response = requests.get(request_url, headers=request_headers)
            response_json = response.json()
            company = response_json['data']['header']['custName']
            job_title = response_json['data']['header']['jobName']
            job_desc = response_json['data']['jobDetail']['jobDescription']
            job_desc = re.sub("\n|\r", "", job_desc)
            job_data = {
                'jdSource': '104人力銀行',
                'company': company,
                'jobTitle': job_title,
                'jobDesc': job_desc
            }
            job_descriptions.append(job_data)
            print("正在爬取{}的{}工作描述...".format(company, job_title))
            sleep_time = random.randint(1, 5)
            time.sleep(sleep_time)
            out = pd.DataFrame(job_descriptions)
        return out