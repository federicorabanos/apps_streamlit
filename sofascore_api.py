import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import json
import time
import random
from faker import Faker
import pandas as pd
from functools import lru_cache
import numpy as np
driver = uc.Chrome(version_main=144)

class SofaAPI:
    def __init__(self):
        self.base_url = "https://api.sofascore.com/api/v1"
        self.driver = None
        self.fake = Faker()

    def _get_driver(self):
        if self.driver is None:
            chrome_options = uc.ChromeOptions()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={self.fake.chrome()}")
            self.driver = uc.Chrome(options=chrome_options)
        return self.driver

    def sofascore_request(self, path):
        path = path.lstrip("/")
        url = f"{self.base_url}/{path}"
        driver = self._get_driver()
        driver.get(url)
        time.sleep(random.uniform(1, 2))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        data = json.loads(soup.text)

        return data


api = SofaAPI()

@lru_cache(maxsize=None)
def cached_request(path):
    return api.sofascore_request(path)