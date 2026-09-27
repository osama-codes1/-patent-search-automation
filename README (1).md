# Patent Search Automation Tool

A Python automation script that searches for patent documents on
[FIPS](https://www.fips.ru) (the Russian Federal Institute of Industrial
Property, similar to the USPTO) and saves the results locally — without any
manual browsing.

## What it does

1. Launches a real Chrome browser session (via Selenium)
2. Opens the FIPS search page and submits a query
3. Collects and lists all matching result links
4. Opens the document the user selects from the list
5. Saves the result as:
   - A **PDF** (a screenshot of the page), and/or
   - A **CSV** file with the title, link, search date, and page text

## Why this project

This was originally a university assignment on office/workflow automation.
It demonstrates:
- Browser automation with **Selenium**
- Parsing and de-duplicating dynamic web content
- Exporting structured data to **CSV**
- Basic image handling with **Pillow**

## Tech stack

- Python 3
- Selenium
- webdriver-manager (automatically installs the matching ChromeDriver)
- Pillow (for saving screenshots as PDF)

## Setup

```bash
pip install -r requirements.txt
```

You'll also need **Google Chrome** installed on your machine — `webdriver-manager`
takes care of downloading the matching ChromeDriver automatically.

## Usage

```bash
python patent_search.py
```

You'll be prompted to:
1. Enter a search query
2. Choose which fields to include in the CSV output
3. Pick a result to open from the list
4. Choose whether to save a PDF and/or CSV of the result

## Example

```
PATENT DOCUMENT SEARCH

Enter search query: solar panel

Results found:
1. Solar panel mounting system --- https://www.fips.ru/...
2. Photovoltaic solar panel --- https://www.fips.ru/...

Enter the number of the result to open: 1
Save as PDF? (yes/no): yes
Save as CSV? (yes/no): yes

Done
```

## Notes

- The browser runs in normal (non-headless) mode by default so you can watch
  it work; pass `headless=True` when creating `PatentSearch` to run it silently.
- This project focuses on the automation logic rather than production
  hardening — selectors may need updates if FIPS changes its page structure.
