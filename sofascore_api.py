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
            driver = self._get_driver()
            
            try:
                driver.get(url)
                # Esperamos un poco más para que el contenido cargue
                time.sleep(random.uniform(2.0, 3.5))
    
                # Extraemos el texto crudo del body
                page_content = driver.find_element(uc.By.TAG_NAME, 'body').text
                
                # Si el contenido está vacío, intentamos con BeautifulSoup como plan B
                if not page_content:
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    page_content = soup.text
    
                # Intentamos cargar el JSON
                data = json.loads(page_content)
                return data
                
            except Exception as e:
                # Esto aparecerá en los logs de Streamlit para que sepas qué pasó
                print(f"Error en request a {path}: {str(e)}")
                return {"error": str(e), "content_preview": page_content[:100] if 'page_content' in locals() else "N/A"}

# Para usarlo en app.py:
# api = SofaAPI() # Esto ahora es seguro porque no crea el driver hasta que se llama a request
