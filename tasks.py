import time, os, zipfile
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


def download_file() -> str:
    """download most recently file from INPI"""
    browser_lib.wait_until_page_contains_element("//table[@class='table table-text-center table-condensed table-bordered table-middle']/tbody")
    browser_lib.wait_until_element_is_visible("//table//tbody/tr[@class='warning']/td[7]/div/a[2]")
    link_el = browser_lib.find_element("//table//tbody/tr[@class='warning']/td[7]/div/a[2]")
    link_str = browser_lib.get_element_attribute(link_el, "href")
    filename = str(link_str).split("/")[-1]
    link_el.click()
    while not Path(DOWNLOAD_DIR).joinpath(filename).is_file():
        time.sleep(1)
    print(" [x] file downloaded succefully")
    browser_lib.close_window()
    browser_lib.close_browser()
    return filename


def search_protocols(file: str):
    """search protocols in file and update protocol status in Base if found"""
    filename, ext = file.split(".")
    protocol_list = []
    # print(users_db.fetch())
    for user in users_db.fetch():
        print(user)
    #     protocols = user.get("protocols", [])
    #     protocol_list.append(protocol["id"] for protocol in protocols)
    # with zipfile.ZipFile(Path(DOWNLOAD_DIR).joinpath(file), "r") as zip:
    #     with zip.open(f"{filename}.xml") as file:
    #         for line in file:
    #             for protocol in protocol_list:
    #                 if protocol in line:
    #                     users_db.
    return


def main():
    try:
        # open_website("http://revistas.inpi.gov.br/rpi/")
        # file = download_file()
        search_protocols("file.t")
    finally:
        browser_lib.close_all_browsers()
    print(f"--- {time.time() - start_time} seconds ---")


if __name__ == "__main__":
    main()
