import csv
import requests
from bs4 import BeautifulSoup
import re

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


def getWebsite(url, redirect):
    try:
        response = requests.get(url, allow_redirects=redirect)
        if response.status_code == 404:
            response.close()
            return ""
        elif response.status_code == 301:
            return getWebsite(url, True)
        else:
            if response.text != "":
                return response.text
            else:
                response.close()
                return ""
    except:
        return ""


# Open the CSV file containing the list of company names
with open("companies.csv") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        company_url = row[1]
        if company_url != "":
            search = re.search("(?:www\.)(.*?)\.", company_url)
            if search != None:
                company_name = search.group(1)
                found_company = False
                for url in urls:
                    format_url = url.replace("{company_name}", company_name)
                    result = getWebsite(format_url, False)
                    if result != "":
                        found_company = True
                        break

                if found_company == False:
                    print(f"{row[0]}: could not find investor urls")
                else:
                    print(f"{row[0]}: found investor urls")
        #
        # print(search)
        # company_name = search.group(1)
        # print(company_name)
