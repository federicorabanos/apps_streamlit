import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import json
import time
import random
from faker import Faker

class SofaAPI:
    def __init__(self):
        self.base_url = "https://api.sofascore.com/api/v1"
        self.driver = None
        self.fake = Faker()

    def _get_driver(self):
        """Inicializa el driver solo cuando se necesita, con opciones para la nube."""
        if self.driver is None:
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            options.add_argument(f'user-agent={self.fake.chrome()}')
            
            # Sin version_main para que se adapte al Chromium del servidor
            self.driver = uc.Chrome(options=options)
        return self.driver

    def sofascore_request(self, path):
        path = path.lstrip("/")
        url = f"{self.base_url}/{path}"
        driver = self._get_driver()
        
        try:
            driver.get(url)
            # Tiempo de espera humano para evitar bloqueos
            time.sleep(random.uniform(2.0, 3.5))

            # Intentamos obtener el texto del body directamente
            page_content = driver.find_element(uc.By.TAG_NAME, 'body').text
            
            # Si el body está vacío, usamos BeautifulSoup como respaldo
            if not page_content:
                soup = BeautifulSoup(driver.page_source, "html.parser")
                page_content = soup.text

            return json.loads(page_content)
        except Exception as e:
            return {"error": str(e)}

    def quit(self):
        if self.driver:
            self.driver.quit()
