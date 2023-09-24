from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver import ChromeOptions, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
from time import sleep
import variables as g

target_url = "https://twitter.com/search?q=%23ぼ喜多&src=typed_query&f=live"


def scrapeSearch():
    print("starting scrape")
    while True:
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        driver = webdriver.Chrome(options=options)

        driver.get(target_url)

        username = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'input[autocomplete="username"]')
            )
        )
        username.send_keys("9086564038")
        username.send_keys(Keys.ENTER)

        password = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'input[name="password"]')
            )
        )
        password.send_keys("M4d3in4byss39")
        password.send_keys(Keys.ENTER)

        time.sleep(5)

        resp = driver.page_source

        soup = BeautifulSoup(resp, "html.parser")

        first_result = soup.find("div", {"data-testid": "cellInnerDiv"})
        first_result_children = first_result.find_all()

        for child in first_result_children:
            if child.has_attr("href"):
                link = child.get("href")
                if "status" in link:
                    print("status found")
                    link = "https://twitter.com" + link
                    f = open("recentlink.txt", "r")
                    lastLink = f.read()
                    if lastLink == link:
                        driver.close()
                        print(link)
                        link = "No new posts"
                        g.newSearchPost = False
                    else:
                        f = open("recentlink.txt", "w")
                        f.write(link)
                        print(link)
                        driver.close()
                        g.newSearchPost = True
                    break
        print(g.searchInterval)
        sleep(g.searchInterval)
