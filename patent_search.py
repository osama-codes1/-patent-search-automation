"""
Patent Search Automation Tool

Automates searching for patents on the FIPS website (the Russian Federal
Institute of Industrial Property, fips.ru) using Selenium. Instead of a user
manually opening the site, typing a search term, and saving the result page,
this tool does it all automatically:

1. Opens the FIPS search page in a real Chrome browser
2. Submits a search query
3. Collects and lists all matching result links
4. Opens the document the user selects
5. Optionally saves the page as a PDF (screenshot) and/or a CSV summary
"""

import os
import re
import csv
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from PIL import Image


class PatentSearch:
    """Automates searching and saving patent documents from fips.ru."""

    SEARCH_URL = "https://www.fips.ru/iiss/search.xhtml"

    def __init__(self, headless: bool = False):
        options = Options()
        options.add_argument("--window-size=1920,1080")
        if headless:
            
            options.add_argument("--headless=new")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        self.saved_title = ""
        self.saved_link = ""
        self.saved_text = ""
        self.saved_time = ""

    def open_site(self):
        """Open the FIPS search page."""
        print("[1] Opening the FIPS website")
        self.driver.get(self.SEARCH_URL)
        time.sleep(3)

    def _find_search_input(self):
        """Locate the search input field on the page."""
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        for el in inputs:
            input_type = (el.get_attribute("type") or "").lower()
            if input_type in ("text", "search"):
                return el
        return None

    def search(self, query: str) -> list[dict]:
        """Submit a search query and return the list of unique result links."""
        print("[2] Running search")
        field = self._find_search_input()
        if field is None:
            return []

        field.clear()
        field.send_keys(query)
        field.send_keys(Keys.ENTER)
        time.sleep(5)

        links = self.driver.find_elements(By.TAG_NAME, "a")
        results = []
        for link in links:
            try:
                href = link.get_attribute("href")
                text = (link.text or "").strip()
                if href and "id=" in href:
                    results.append({
                        "title": text if text else "Untitled",
                        "url": href
                    })
            except Exception:
                continue

        
        unique = {}
        for r in results:
            unique[r["url"]] = r
        return list(unique.values())

    def open_selected_document(self, selected: dict) -> bool:
        """Open a chosen result and store its title, link, and page text."""
        href = selected["url"]
        title = selected["title"]

        print(f"[3] Opening selected document: {title}")
        self.driver.get(href)
        time.sleep(3)

        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        lowered = body_text.lower()
        if "page not found" in lowered or "404" in lowered:
            return False

        self.saved_title = title
        self.saved_link = href
        self.saved_text = body_text
        self.saved_time = datetime.now().strftime("%d.%m.%Y %H:%M")
        return True

    @staticmethod
    def _safe_filename(name: str, max_len: int = 80) -> str:
        """Turn a string into a filesystem-safe filename."""
        name = re.sub(r'[\\/:*?"<>|]+', "_", name)
        name = name.strip().strip(".")
        return (name[:max_len] if len(name) > max_len else name) or "document"

    def save_csv(self, fields: list[str], filename: str | None = None):
        """Save the currently loaded document's data as a CSV file."""
        print("[4] Saving CSV")

        allowed = {"Title", "Link", "Search Date", "Page Text"}
        fields = [f for f in fields if f in allowed]
        if not fields:
            fields = ["Title", "Link", "Search Date"]

        data = {
            "Title": self.saved_title,
            "Link": self.saved_link,
            "Search Date": self.saved_time,
            "Page Text": self.saved_text[:3000],  
        }

        if filename is None:
            base = self._safe_filename(self.saved_title)
            filename = f"result_{base}.csv"

        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerow({k: data.get(k, "") for k in fields})

        print(f"CSV saved: {os.path.abspath(filename)}")

    def save_pdf(self, filename: str | None = None):
        """Save a screenshot of the currently loaded page as a PDF."""
        print("[5] Saving PDF")

        if filename is None:
            base = self._safe_filename(self.saved_title)
            filename = f"page_{base}.pdf"

        temp_png = "page_tmp.png"
        self.driver.save_screenshot(temp_png)

        img = Image.open(temp_png)
        img.convert("RGB").save(filename)
        os.remove(temp_png)

        print(f"PDF saved: {os.path.abspath(filename)}")

    def close(self):
        """Close the browser."""
        self.driver.quit()


def main():
    print("PATENT DOCUMENT SEARCH")

    query = input("\nEnter search query: ").strip()
    if not query:
        print("Empty query. Exiting.")
        return

    print("\nWhich fields should be saved in the CSV?")
    print("Title, Link, Search Date, Page Text")
    raw = input("Enter them separated by commas: ").strip()
    fields = [x.strip() for x in raw.split(",") if x.strip()]

    search = PatentSearch(headless=False)
    try:
        search.open_site()

        results = search.search(query)
        if not results:
            print("No documents found")
            return

        print("\nResults found:")
        for i, res in enumerate(results, 1):
            print(f"{i}. {res['title']} --- {res['url']}")

        choice = 1
        if len(results) > 1:
            while True:
                try:
                    choice = int(input("\nEnter the number of the result to open: ").strip())
                    if 1 <= choice <= len(results):
                        break
                    print("Invalid number")
                except ValueError:
                    print("Please enter a number")

        selected = results[choice - 1]
        if not search.open_selected_document(selected):
            print("Could not open the document")
            return

        if input("\nSave as PDF? (yes/no): ").strip().lower() in ("yes", "y"):
            search.save_pdf()

        if input("Save as CSV? (yes/no): ").strip().lower() in ("yes", "y"):
            search.save_csv(fields)

        print("\nDone")

    finally:
        search.close()


if __name__ == "__main__":
    main()
