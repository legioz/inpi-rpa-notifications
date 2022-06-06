import time, os
from deta import Deta
from pathlib import Path
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from dotenv import load_dotenv
from webdriver_manager.firefox import GeckoDriverManager

load_dotenv()

PROJECT_KEY = os.environ.get("PROJECT_KEY", None)
DOWNLOAD_DIR = "download"
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
deta = Deta(PROJECT_KEY)
users_db = deta.Base("users")
browser_lib = Selenium()
start_time = time.time()


def open_website(url):
    """download driver and opens the browser"""
    driver_path = GeckoDriverManager().install()
    mime_types = "application/pdf"
    options = browser_lib._get_driver_args("firefox")[0]["options"]
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)
    options.set_preference(
        "browser.download.dir", Path(DOWNLOAD_DIR).resolve(strict=True).__str__()
    )
    options.set_preference("pdfjs.disabled", True)
    options.set_preference("browser.link.open_newwindow", 3)
    options.set_preference("browser.link.open_newwindow.restriction", 0)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_types)
    options.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
    browser_lib.open_browser(
        url, browser="firefox", options=options, executable_path=driver_path
    )


def download_file():
    """clear all files and download most recently file from INPI"""


def search_protocols():
    """search protocols in file and update protocol status in Base if found"""


def main():
    try:
        open_website("http://revistas.inpi.gov.br/rpi/")
        download_file()
        search_protocols
    finally:
        browser_lib.close_all_browsers()
    print(f"--- {time.time() - start_time} seconds ---")


if __name__ == "__main__":
    main()
