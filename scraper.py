from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

import time
import re
import subprocess

HOST = "https://www.portaleargo.it/argoweb/famiglia/index1.jsp"
URL = "https://www.portaleargo.it/auth/sso/login"

def scrap_grades(username: str, password: str, school_code: str) -> tuple[list, list]:

    ## For snap: ##
    isChrome = False

    if not isChrome:
        try:
            snap = subprocess.check_output(["snap", "--version"])
            print("Snap is installed, version:", snap.decode().strip())
            isSnap = True
        except FileNotFoundError:
            print("Snap is not installed")
            isSnap = False

        if isSnap:
            firefox_bin = "/snap/firefox/current/usr/lib/firefox/firefox"
            firefoxdriver_bin = "/snap/firefox/current/usr/lib/firefox/geckodriver"

            options = Options()
            options.add_argument("--headless")
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.binary_location = firefox_bin
            service = Service(executable_path=firefoxdriver_bin)
            driver = webdriver.Firefox(options=options, service=service)

        else:
            options = Options()
            options.add_argument("--headless")
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Firefox(options=options)
    else:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)

    driver.get(HOST)

    form = driver.find_element(By.NAME, "loginForm")
    form.find_element(By.NAME, "famiglia_customer_code").send_keys(school_code)
    form.find_element(By.NAME, "username").send_keys(username)
    form.find_element(By.NAME, "password").send_keys(password)

    driver.find_element(By.NAME, "login").click()

    _found = False
    while not _found: # Decorator?
        try:
            driver.find_element(By.ID, "menu-servizialunno:voti-giornalieri").click()
            _found = True
            # print("Element found")
        except:
            time.sleep(1)

    _found = False
    while not _found:
        try:
            table = driver.find_element(By.ID, "sheet-sezioneDidargo:sheet")
            _found = True
        except:
            time.sleep(1)

    subjects = table.find_elements(By.TAG_NAME, "legend")
    subjects = list(map(lambda subj: subj.text, subjects))

    # print(subjects)

    content = table.text.split("\n")
    content = list(map(lambda i: " ".join(i.strip().split()), content))
    # print(content)

    driver.quit()

    return content, subjects

def extract_grades(raw_grades: list, subjects: list) -> dict:

    grades = {}
    current_subj = current_date = current_value = None
    current_weight = "100%"

    for i in raw_grades:
        if i in subjects:
            if current_value and current_date and current_subj:
                grades[current_subj].append({"value": current_value, "weight": current_weight, "date": current_date})
                current_value = None
                current_weight = "100%"
                current_date = None
            current_subj = i
            grades[current_subj] = []
            continue

        date = re.search(r'[0-9]+/+[0-9]+/+[0-9]+', i)
        mark = re.search(r'\([0-9]+\.[0-9]+\)', i)
        weight = re.search(r'[0-9]+%{1}', i)
        if mark and current_value:
            grades[current_subj].append({"value": current_value, "weight": current_weight, "date": current_date})
            current_value = mark.group(0).replace("(", "").replace(")", "")
        if mark:
            current_value = mark.group(0).replace("(", "").replace(")", "")
        if weight:
            current_weight = weight.group(0)
        if date:
            if current_value and current_date:
                grades[current_subj].append({"value": current_value, "weight": current_weight, "date": current_date})
                current_value = None
                current_weight = "100%"
            current_date = date.group(0)

    return grades

def get_grades(username: str, password: str, school_code: str):

    content, subjects = scrap_grades(username, password, school_code)
    grades = extract_grades(content, subjects)

    return grades