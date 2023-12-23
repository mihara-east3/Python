import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd

"""
## Web scraping on Streamlit Cloud with Selenium

[![Source](https://img.shields.io/badge/View-Source-<COLOR>.svg)](https://github.com/snehankekre/streamlit-selenium-chrome/)

This is a minimal, reproducible example of how to scrape the web with Selenium and Chrome on Streamlit's Community Cloud.

Fork this repo, and edit `/streamlit_app.py` to customize this app to your heart's desire. :heart:
"""

with st.echo():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    # Options for Chrome driver
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_experimental_option("detach", True)

    # Define get_driver function
    @st.cache_resource
    def get_driver():
        return webdriver.Chrome(options=options)

    # Initialize driver
    driver = get_driver()
    driver.get("https://hjks.jepx.or.jp/hjks/outages")

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Find the grid-data and make DataFrame
    grid_data = soup.find_all('div', class_='w2ui-grid-data')
    rows = []
    for data in grid_data:
        cell_data = [cell.text.strip() for cell in data.find_all('div', class_='w2ui-grid-data')]
        rows.append(cell_data)

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    st.dataframe(df)