import os
import time

import fire
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By

URL = "https://portal.wiwi.kit.edu/ys"

SIGN_IN_LINK_XPATH = '//*[@id="main_content"]/div/div[2]/a'
USERNAME_INPUT_XPATH = '//*[@id="username"]'
PASSWORD_INPUT_XPATH = '//*[@id="password"]'
LOGIN_BUTTON_XPATH = '//*[@id="sbmt"]'
FACULTY_SELECTION_XPATH = '//*[@id="filterPanel"]/div[2]/div/div[2]/div[1]/select[2]'
SEARCH_XPATH = '//*[@id="filterPanel"]/div[2]/div/div[2]/div[2]/input'
FILTER_BACHELOR_CHECKBOX_XPATH = '//*[@id="filterPanel"]/div[2]/div/div[2]/div[4]/div[1]'
FILTER_MASTER_CHECKBOX_XPATH = '//*[@id="filterMaster"]'
FILTER_DIPLOM_CHECKBOX_XPATH = '//*[@id="filterDiplom"]'
TABLE_XPATH = '/html/body/main/section[3]/div/div/div/div[3]/div/table'

options = Options()
# options.add_argument("--headless=new")

service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def _wait_for_element_presence(xpath: str):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))


def _find_element(xpath: str):
    _wait_for_element_presence(xpath=xpath)
    return driver.find_element(By.XPATH, xpath)


def _click(xpath: str):
    ele = _find_element(xpath)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    ele.click()


def _type_into_input(xpath: str, text: str):
    ele = _find_element(xpath)
    ele.clear()
    ele.send_keys(text)


def _handle_select(xpath: str, visible_text: str):
    ele = Select(_find_element(xpath))
    ele.select_by_visible_text(visible_text)
    time.sleep(10)


def _check_and_log_table_entries(xpath: str):
    found_at_least_one = False
    table_ele = _find_element(xpath)
    rows = table_ele.find_elements(By.XPATH, ".//tr")
    if len(rows) > 1:
        for row in rows[1:]:
            columns = row.find_elements(By.XPATH, ".//td")
            bezeichnung_col = columns[2]
            link_ele = bezeichnung_col.find_element(By.XPATH, ".//a")
            text, link = link_ele.text, link_ele.get_attribute("href")

            logger.info(f"Found a seminar '{text}'")
            logger.info(f"\tLink: {link}")
            found_at_least_one = True
    else:
        logger.warning("Did not find any entries in table...")

    if found_at_least_one:
        raise ValueError("Found at least one seminar. Go check it out")


def main(url: str, faculty: str = None, filter_text: str = None):
    driver.get(url)  # Signin link
    _click(SIGN_IN_LINK_XPATH)
    _type_into_input(USERNAME_INPUT_XPATH, os.environ["USERNAME"])
    _type_into_input(PASSWORD_INPUT_XPATH, os.environ["PASSWORD"])
    _find_element(LOGIN_BUTTON_XPATH).click()

    _handle_select(FACULTY_SELECTION_XPATH, faculty)

    if filter_text:
        _type_into_input(SEARCH_XPATH, filter_text)
    _check_and_log_table_entries(TABLE_XPATH)
    driver.quit()


if __name__ == '__main__':
    fire.Fire(main)
