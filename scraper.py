from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

import time
import re
import subprocess
import json

HOST = "https://www.portaleargo.it/argoweb/famiglia/index1.jsp"

def read_grades(driver) -> map:

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
            table = driver.find_element(By.ID, "sheet-sezioneDidargo:panel-votiGiornalieri:pannello")
            _found = True
        except:
            time.sleep(1)


    subtables = table.find_elements(By.TAG_NAME, "fieldset")
    content = {}

    for subtable in subtables:
        subject = subtable.find_element(By.TAG_NAME, "legend").text

        rows = subtable.find_elements(By.TAG_NAME, "tr")
        rows = list(map(lambda row: row.text, rows))
        rows = list(map(lambda i: i.strip().replace("\n", ""), rows))

        # print(rows)

        content[subject] = rows

    try:
        exit = driver.find_element(By.CLASS_NAME, "btl-modal-closeButton").click()
        time.sleep(0.5)
    except:
        print("Error on closing marks tab")
        pass
    # print(content)
    return content


def scrap_grades(username: str, password: str, school_code: str) -> map | list[map]:

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
            # options.add_argument("--headless")
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
    while not _found: # Just to wait for the page to be loaded
        try:
            driver.find_element(By.ID, "menu-servizialunno:voti-giornalieri")
            _found = True
        except:
            time.sleep(1)

    try:
        change_class = driver.find_element(By.ID, "cambio-classe")
        change_class.find_element(By.TAG_NAME, "table").click()

        time.sleep(0.5)
        years_tab = driver.find_element(By.ID, "_idJsp58")
        years_table = years_tab.find_elements(By.TAG_NAME, "table")[-1]
        cells = years_table.find_elements(By.TAG_NAME, "td")

        contents = []
        
        for i in range(len(cells) // 2):
            cells[2*i].click()
            content = read_grades(driver)
            contents.append({cells[2*i].text: content})

            change_class = driver.find_element(By.ID, "cambio-classe")
            change_class.find_element(By.TAG_NAME, "table").click()
        
        print(contents)
        time.sleep(50)

    except:
        print("Change class not found")
        pass

    content = read_grades(driver)

    driver.quit()

    return content

def extract_grades(raw_grades: dict) -> dict:

    grades = {}

    for subject in raw_grades:
        grades[subject] = []
        for test in raw_grades[subject]:

            obj = {}

            date = re.search(r'[0-9]{1,2}/+[0-9]{1,2}/+[0-9]+', test)
            mark = re.search(r'\([0-9]+\.[0-9]+\)', test)
            weight = re.search(r'[0-9]+%{1}', test)

            if mark == None:
                continue
            else:
                obj["value"] = mark.group(0).replace("(", "").replace(")", "")
            if weight == None:
                obj["weight"] = "100%"
            else:
                obj["weight"] = weight.group(0)
            if date == None:
                obj["date"] = "10/09/2024"
            else:
                obj["date"] = date.group(0)

            grades[subject].append(obj)

    return grades

def get_grades(username: str, password: str, school_code: str):

    content = scrap_grades(username, password, school_code)
    grades = extract_grades(content)

    with open('./output/grades.json', 'w') as f:
        json.dump(grades, f, indent=2)

    return grades