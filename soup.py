import time
import csv
import requests
from bs4 import BeautifulSoup
import re
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from seleniumwire.utils import decode
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

options = webdriver.ChromeOptions()
# options.add_argument("--auto-open-devtools-for-tabs")

urls = [
    "https://{company_name}.com/investor-relations",
    "https://investor.{company_name}.com",
    "https://{company_name}.com/about-us/investors",
    "https://{company_name}.com/investors",
    "https://{company_name}.com/investors.html",
    "https://{company_name}.com/about/investor-relations",
    "https://investors.{company_name}.com/home/default.aspx",
    "https://investors.{company_name}.com",
    "https://investors.{company_name}.com/ir-home/default.aspx",
    "https://{company_name}.com/corporate/investor-relations",
    "https://{company_name}.com/en/investor-relations",
]

# Define a list of keywords to look for in the file names
keywords = ["earnings", "conference", "call"]
# Create a list to store the URLs of earnings call audio and video files
ir_links = []


def getWebsite(driver, url, company_name, ticker, count=0):
    driver.set_page_load_timeout(30)
    try:
        driver.get(url)
        count = 0
        sites = []
        for request in driver.requests:
            if request.response:
                find_param = company_name + ".com"
                if find_param in request.url:
                    if request.response.headers["Content-Type"]:
                        if "text/html" in request.response.headers["Content-Type"]:
                            if "track" not in request.url:
                                sites.append(request)

        del driver.requests

        for site in sites:
            if site.response.status_code == 200:
                if "404" in site.url:
                    return ""
                body = decode(
                    site.response.body,
                    site.response.headers.get("Content-Encoding", "identity"),
                )
                content_type = site.response.headers["Content-Type"]
                splt = content_type.split("charset=")
                if len(splt) > 1:
                    encoding = content_type.split("charset=")[1]
                    body = str(body, encoding)
                    if "page not found" in body.lower():
                        return ""
                    search = re.search("(?:E|e)arnings?", body)
                    if search != None:
                        return site.url
                    else:
                        search = re.search("Q(?:1|2|3|4)", body)
                        if search != None:
                            return site.url
                        else:
                            search = re.search("(?:F|f)iscal", body)
                            if search != None:
                                return site.url
                            else:
                                search = re.search("(?:S|s)tock", body)
                                if search != None:
                                    return site.url
                                else:
                                    search_str = f"(?:NYSE|NASDAQ):\s?{ticker}"
                                    print(search_str)
                                    search = re.search(search_str, body)
                                    if search != None:
                                        return site.url

        return ""
    except TimeoutException:
        print("timeout")
        if count >= 5:
            return ""
        count = count + 1
        print("retrying")
        return getWebsite(driver, url, company_name, ticker, count)
    except Exception as e:
        print(e)
        return ""


good_urls = dict()
missing_urls = []

# Open the CSV file containing the list of company names
with open("companies.csv") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        company_url = row[1]
        ticker = row[2]
        if company_url != "":
            if ".com" in company_url:
                search = re.search("(?:www\.)(.*?)\.", company_url)
                if search != None:
                    driver = webdriver.Chrome(options=options)
                    company_name = search.group(1)
                    found_company = False

                    for url in urls:
                        format_url = url.replace("{company_name}", company_name)
                        print(format_url)
                        result = getWebsite(driver, format_url, company_name, ticker)
                        if result != "":
                            good_urls[row[0]] = result
                            found_company = True
                            break
                        # driver.find_element(by=)

                    if found_company == False:
                        missing_urls.append(row[0])
                    driver.quit()
            else:
                search = re.search("(?:www\.)(.*?)\.(.*?)\/", company_url)
                if search != None:
                    driver = webdriver.Chrome(options=options)
                    company_name = search.group(1)
                    extension = search.group(2)
                    found_company = False

                    for url in urls:
                        format_url = url.replace("{company_name}", company_name)
                        format_url = format_url.replace(".com", "." + extension)
                        result = getWebsite(driver, format_url, company_name, ticker)
                        if result != "":
                            good_urls[row[0]] = result
                            found_company = True
                            break

                    if found_company == False:
                        missing_urls.append(row[0])
                    driver.quit()


print("Good URLs")
for key, value in good_urls.items():
    print(key, value)

print("Missing URLs")
for url in missing_urls:
    print(url)
