"""
To Prepare and send a request to the Pro version, subsequently receive the response
"""
import re
import requests

from .BugBounty import HandleResponse
from .handlers import PDFSpliter
from .helpers import *


class GoPro(object):
    def __init__(self, api_key):
        """API Key received from extracttable.com"""
        self.api_key = api_key
        self.basic_validation()
        self.headers = {"x-api-key": self.api_key}
        self.api_usage = {}

    def basic_validation(self):
        if not self.api_key:
            notify(free_api_key)
            raise ValueError('"api_key" is needed in "pro_kwargs"')
        elif any([len(self.api_key) not in range(30, 129), re.search(r"A-Za-z0-9", self.api_key)]):
            notify(free_api_key)
            raise ValueError("Invalid api_key received. Please check api_key")

    def validate_api_key(self):
        valid = requests.get(validate_api_key_url, headers=self.headers)
        if not valid:
            print("#-# " * 12)
            for k, v in valid.json().items():
                print(k, ":", v)
            print("#-#" * 12)
            raise ValueError(valid.json()["Message"])

        self.api_usage = valid.json()['usage']

        return self.check_credit_usage()

    def check_credit_usage(self):
        info_user_credit_threshold = 50
        credits_left = self.api_usage['credits'] - (self.api_usage['used'] + self.api_usage['queued'])
        if 0 < credits_left < info_user_credit_threshold:
            print(f"[Info]: Only {credits_left} Credits Left")
        elif credits_left <= 0:
            notify(out_of_credits)
            print("API Credits Usage Info Below:")
            for k, v in self.api_usage.items():
                print(f"{k}: {v}")
            return False

        return self

    def trigger(self, filepath, pages, password: str = "", dup_check: bool = False) -> dict:
        """
        Trigger the file to the server for table extraction process
        :param filepath: location of the input file
        :param pages: str, optional (default: '1')
            Comma-separated page numbers.
            Example: '1,3,4' or '1,4-end' or 'all'.
        :param password : str, optional (default: None)
            Password for decryption
        :param dup_check: to handle idempotent requests; default to False
        :return:
        """
        with PDFSpliter(filepath, pages, password) as pdf_obj:
            with open(pdf_obj.filepath, 'rb') as infile:
                files = {'input': infile}
                data = {"dup_check": dup_check}
                triggered = requests.post(trigger_url, files=files, data=data, headers=self.headers)
                HandleResponse(triggered)
        return triggered.json()

    def get_tables(self, job_id: str) -> dict:
        """
        Retrieve the job result from the endpoint
        :param: job_id: JobId from the Triggered response
        """
        retreive = requests.get(job_info_url, params={"JobId": job_id}, headers=self.headers)
        HandleResponse(retreive)
        return retreive.json()
