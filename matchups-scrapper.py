from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import csv
import time
import logging
import random
import os
import undetected_chromedriver as uc
from urllib.parse import urlparse

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    try:
        # Usar undetected-chromedriver para evitar detecção
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        
        # Configurações adicionais anti-bloqueio
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        
        driver = uc.Chrome(options=options)
        return driver
    except Exception as e:
        logging.error(f"Erro ao configurar o driver: {str(e)}")
        raise

def simulate_human_behavior(driver):
    """Simula comportamentos humanos para evitar detecção"""
    try:
        # Rolagem suave
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(random.uniform(0.5, 1.0))
        driver.execute_script("window.scrollTo(300, 600);")
        time.sleep(random.uniform(0.5, 1.0))
        driver.execute_script("window.scrollTo(600, 300);")
        time.sleep(random.uniform(0.5, 1.0))
        driver.execute_script("window.scrollTo(300, 0);")
        
    except Exception as e:
        logging.warning(f"Erro ao simular comportamento humano: {str(e)}")

def main():
    driver = None
    try:
        # Obter o diretório atual do projeto
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file = os.path.join(current_dir, "mlb_pitcher_props_urls.csv")
        
        logging.info(f"Diretório atual do projeto: {current_dir}")
        logging.info(f"Caminho do arquivo CSV: {csv_file}")
        
        driver = setup_driver()
        url = "https://sportsbook.fanduel.com/navigation/mlb"
        logging.info(f"Acessando URL: {url}")
        
        driver.get(url)
        time.sleep(5)
        
        simulate_human_behavior(driver)
        
        page_source = driver.page_source
        if "verify" in page_source.lower() or "human" in page_source.lower():
            logging.error("Página de verificação detectada. Tentando contornar...")
            driver.refresh()
            time.sleep(5)
            simulate_human_behavior(driver)
        
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )
        except Exception as e:
            logging.warning(f"Tempo de espera excedido, mas continuando: {str(e)}")
        
        all_links = driver.find_elements(By.TAG_NAME, "a")
        logging.info(f"Total de links encontrados na página: {len(all_links)}")
        
        urls = []
        
        for link in all_links:
            try:
                href = link.get_attribute("href")
                if href:
                    # Se o link for relativo
                    if href.startswith("/"):
                        full_href = f"https://sportsbook.fanduel.com{href}"
                        if "/baseball/mlb" in full_href:
                            urls.append(full_href)
                            logging.info(f"Link MLB encontrado: {full_href}")
                    # Se o link já for absoluto
                    elif "fanduel.com" in href:
                        if "/baseball/mlb" in href:
                            urls.append(href)
                            logging.info(f"Link MLB encontrado: {href}")
                    
            except Exception as e:
                logging.warning(f"Erro ao processar link: {str(e)}")
                continue
        
        if not urls:
            logging.error("Nenhum link MLB foi encontrado. Verificando o conteúdo da página...")
            logging.info(f"Conteúdo da página: {driver.page_source[:500]}")  # Mostra os primeiros 500 caracteres
            return
        
        unique_urls = []
        for url in urls:
            if url not in unique_urls:
                unique_urls.append(url)
        
        try:
            with open(csv_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                for url in unique_urls:
                    modified_url = f"{url}?tab=pitcher-props"
                    writer.writerow([modified_url])
            
            if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
                logging.info(f"Arquivo CSV criado com sucesso: {csv_file}")
                logging.info(f"Total de URLs MLB extraídas: {len(unique_urls)}")
            else:
                logging.error(f"Falha ao criar o arquivo CSV: {csv_file}")
        
        except Exception as e:
            logging.error(f"Erro ao salvar o arquivo CSV: {str(e)}")
            logging.error(f"Diretório de trabalho atual: {os.getcwd()}")
            logging.error(f"Permissões do diretório: {os.access(current_dir, os.W_OK)}")
            
    except Exception as e:
        logging.error(f"Erro durante a execução: {str(e)}")
    
    finally:
        if driver:
            try:
                driver.quit()
                logging.info("Navegador fechado")
            except Exception as e:
                logging.error(f"Erro ao fechar o navegador: {str(e)}")

if __name__ == "__main__":
    main()