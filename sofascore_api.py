import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import json
import time
import random
from faker import Faker
import pandas as pd
from functools import lru_cache
import numpy as np

# ELIMINAMOS la línea: driver = uc.Chrome(version_main=144) 
# porque eso intenta abrir una ventana normal antes de configurar nada.

class SofaAPI:
    def __init__(self):
        self.base_url = "https://api.sofascore.com/api/v1"
        self.driver = None
        self.fake = Faker()

    def _get_driver(self):
        if self.driver is None:
            chrome_options = uc.ChromeOptions()
            # IMPORTANTE: Configuraciones para servidores (Streamlit Cloud)
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"user-agent={self.fake.chrome()}")
            
            # Dejamos que uc detecte la versión automáticamente
            self.driver = uc.Chrome(options=chrome_options)
        return self.driver

    def sofascore_request(self, path):
        path = path.lstrip("/")
        url = f"{self.base_url}/{path}"
        
        # Obtenemos el driver configurado correctamente
        driver = self._get_driver()
        driver.get(url)
        
        # Un pequeño delay para no ser bloqueados
        time.sleep(random.uniform(1.5, 2.5))

        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            # Sofascore a veces devuelve el JSON dentro de una etiqueta <pre>
            data = json.loads(soup.text)
            return data
        except Exception as e:
            # Si falla, devolvemos un error para que el script principal no muera
            return {"error": str(e)}

# Para usarlo en app.py:
# api = SofaAPI() # Esto ahora es seguro porque no crea el driver hasta que se llama a request