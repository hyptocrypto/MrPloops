from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as webdriver
import urllib


def gen_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    return webdriver.Chrome(
        options=options,
        desired_capabilities={"goog:loggingPrefs": {"performance": "ALL"}},
    )


def scroll_full_page(driver):
    for i in range(5):
        driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
        time.sleep(1)
    elm = driver.find_element(By.XPATH, "//input[@value='Show more results']")
    elm.click()
    time.sleep(1)
    for i in range(5):
        driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
        time.sleep(1)


if __name__ == "__main__":
    driver = gen_driver()
    driver.get(
        "https://www.google.com/search?sca_esv=571916744&q=dogs+pooping&tbm=isch&source=lnms&sa=X&ved=2ahUKEwi_pfDyj-mBAxX1STABHTFyAkUQ0pQJegQIDRAB&biw=1920&bih=995&dpr=1"
    )
    scroll_full_page(driver)
    soup = BeautifulSoup(driver.page_source)
    img_divs = soup.find_all("div", {"class": "fR600b islir"})
    for idx, img in enumerate(img_divs):
        try:
            with urllib.request.urlopen(img.img["src"]) as resp:
                data = resp.read()
                with open(f"imgs/pooping/{idx}.jpeg", "+wb") as f:
                    f.write(data)
        except:
            pass

    driver.get(
        "https://www.google.com/search?q=golden+doodle+pooping&tbm=isch&ved=2ahUKEwjM7eXt1OmBAxUdM1kFHfsZDVMQ2-cCegQIABAA&oq=golden+doodle+pooping&gs_lcp=CgNpbWcQA1AAWABggVBoAHAAeACAAW6IAcIBkgEDMS4xmAEAqgELZ3dzLXdpei1pbWfAAQE&sclient=img&ei=ek8kZczICJ3m5NoP-7O0mAU&bih=926&biw=1200"
    )
    scroll_full_page(driver)
    soup = BeautifulSoup(driver.page_source)
    img_divs = soup.find_all("div", {"class": "fR600b islir"})
    for idx, img in enumerate(img_divs):
        try:
            with urllib.request.urlopen(img.img["src"]) as resp:
                data = resp.read()
                with open(f"imgs/not_pooping/{idx}.jpeg", "+wb") as f:
                    f.write(data)
        except:
            pass
