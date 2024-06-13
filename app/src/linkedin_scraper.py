import random
import time

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

from utils import remove_emojis
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager


class LinkedinScraper:
    def __init__(self):
        load_dotenv()
        self.browser = self._get_browser()

    def _get_browser(self):
        return webdriver.Firefox(service=webdriver.firefox.service.Service(GeckoDriverManager().install()))

    def login(self):
        self.browser.get("https://www.linkedin.com/uas/login")
        self.browser.find_element(By.ID, 'username').send_keys(os.getenv('LINKEDIN_USERNAME'))
        self.browser.find_element(By.ID, 'password').send_keys(os.getenv('LINKEDIN_PASSWORD'))
        self.browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    def check_for_authentication(self):
        try:
            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.ID, 'input__email_verification_pin'))
            )
            print("Page d'authentification détectée. En attente du code de vérification.")
            return True
        except:
            return False

    def ensure_authenticated(self):
        if self.check_for_authentication():
            while self.check_for_authentication():
                time.sleep(15)

    def go_to_search_link(self, link, current_page):
        self.browser.get(f"{link}&page={current_page}")

    def get_all_profiles_on_page(self):
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.reusable-search__result-container')))
        all_profils_list = self.browser.find_elements(By.CSS_SELECTOR,
                                                      'li.reusable-search__result-container')
        all_profils_info = []
        for profile_content in all_profils_list:
            try:
                connect_or_follow = profile_content.find_element(By.CSS_SELECTOR,
                                                                 'div.entity-result__actions.entity-result__divider').text
            except:
                continue
            if connect_or_follow not in ["Se connecter", "Suivre"]:
                continue
            linkedin_profile_link = profile_content.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

            # Modification ici pour le nom complet
            full_name_element = profile_content.find_element(By.CSS_SELECTOR,
                                                             'span.entity-result__title-text a span[dir="ltr"]')
            full_name = full_name_element.text.strip()  # Retire les espaces superflus
            full_name = remove_emojis(full_name)  # Enlève les emojis si nécessaire

            # Extraction du prénom et du nom si possible
            name_parts = full_name.split()
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            profil = {
                "full_name": full_name,
                "first_name": first_name,
                "last_name": last_name,
                "linkedin_profile_link": linkedin_profile_link,
                "connect_or_follow": connect_or_follow
            }
            all_profils_info.append(profil)
        return all_profils_info

    def go_to_profile_page(self, profile_link):
        self.browser.get(profile_link)

    def is_open_to_work(self):
        try:
            profile_image = WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'img.pv-top-card-profile-picture__image')))
            if '#OPEN_TO_WORK' in profile_image.get_attribute('alt'):
                return True
        except:
            return False

    def connect_to_profil(self):
        connect_button = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view.pvs-profile-actions__action')))
        connect_button.click()

    def first_button_text(self): #connaitre le texte du premier bouton d'action sur le profil
        button = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view.pvs-profile-actions__action')))
        return button.text

    def send_invitation_with_message(self, message):
        add_note = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Ajouter une note"]')))
        add_note.click()
        custom_message = WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'custom-message')))
        custom_message.send_keys(message)
        send_invitation = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Envoyer une invitation"]')))
        send_invitation.click()

    def go_to_next_page(self, link, current_page):
        self.browser.get(f"{link}&page={current_page + 1}")

    def wait_random_time(self):
        wait_time = random.uniform(8, 16)
        time.sleep(wait_time)

    def _click_plus(self):
        # Attend que le bouton "Plus" soit présent et cliquable
        plus_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Plus d’actions')]"))
        )
        # Clique sur le bouton "Plus"
        plus_button.click()
        time.sleep(1)  # Petite pause pour laisser le temps à l'interface de réagir
        return

    def click_connect_on_plus(self):
        # Clique sur le bouton "Plus"
        plus_button = WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ph5 .artdeco-dropdown__trigger')))
        plus_button.click()

        # Attends que le menu déroulant soit chargé
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.artdeco-dropdown__content-inner')))

        # Trouve tous les éléments du menu déroulant
        dropdown_items = self.browser.find_elements(By.CSS_SELECTOR, '.artdeco-dropdown__content-inner li div.artdeco-dropdown__item')

        # Trouve l'élément "Se connecter" et clique dessus
        for item in dropdown_items:
            if "Se connecter" in item.text:
                item.click()
                break

    def close_browser(self):
        self.browser.quit()
