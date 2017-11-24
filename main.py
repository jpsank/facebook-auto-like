from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options


class FacebookBot:
    def __init__(self,username,password):
        self.username = username
        self.password = password

        options = Options()
        options.add_argument("--disable-notifications")

        self.wd = webdriver.Chrome(chrome_options=options)
        self.login()

    def login(self):
        self.wd.get("https://www.facebook.com/login")
        self.wd.find_element_by_id("email").send_keys(self.username)
        self.wd.find_element_by_id("pass").send_keys(self.password)
        self.wd.find_element_by_id("loginbutton").click()

    def get_posts(self):
        articles = self.wd.find_elements_by_xpath("//*[@role='article'][not(@data-story_category)]")
        data = []
        for a in articles:
            if a.get_attribute("id").startswith("hyperfeed_story_id_"):
                likeIts = [i.get_attribute("aria-label").split() for i in a.find_elements_by_class_name("_3emk") if i.get_attribute("aria-label")]
                likes = {"Like":0,"Love":0,"Haha":0,"Wow":0,"Sad":0,"Angry":0}
                likes.update({i[1]: int(i[0]) for i in likeIts})
                try:
                    button = a.find_element_by_class_name("UFILikeLink")
                except exceptions.NoSuchElementException:
                    continue
                data.append({"likes":likes,"button":button,"article":a})
        return data

    def scroll(self):
        find_elem = None
        scroll_from = 0
        scroll_limit = self.wd.execute_script("return document.body.scrollHeight")
        while not find_elem:
            self.wd.execute_script("window.scrollTo(%d, %d);" % (scroll_from, scroll_from + scroll_limit))
            scroll_from += scroll_limit
            try:
                find_elem = self.wd.find_element_by_xpath("//span[@class='_38my']")
                find_elem.click()
            except exceptions.ElementNotVisibleException:
                find_elem = None
            except exceptions.NoSuchElementException:
                find_elem = None

    def automate(self,unlike=False):
        self.scroll()
        self.wd.execute_script("window.scrollTo(0,0);")
        posts = self.get_posts()
        for p in posts:
            if p["likes"]["Angry"] == 0 and p["likes"]["Sad"] == 0 and p["likes"]["Like"] > 5:
                article = p["article"]
                self.wd.execute_script("arguments[0].scrollIntoView();", article)
                button = article.find_element_by_class_name("UFILikeLink")
                if button.get_attribute("aria-pressed") == "true" if unlike else "false":
                    self.wd.execute_script("arguments[0].click();",button)
                    print('%s "%s"' % ("Unliked" if unlike else "Liked",article.find_element_by_tag_name("p").get_attribute("innerText").replace("\n"," ")))

    def close(self):
        self.wd.close()


bot = FacebookBot(input("Username: "),input("Password: "))

bot.automate()
bot.close()
