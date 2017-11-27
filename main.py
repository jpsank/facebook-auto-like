from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options


class FacebookBot:
    def __init__(self,username,password,status_report=False):
        self.username = username
        self.password = password

        self.status_report = status_report

        options = Options()
        options.add_argument("--disable-notifications")

        if self.status_report: print("Opening chromedriver...")
        self.wd = webdriver.Chrome(chrome_options=options)
        if self.status_report: print("Logging in...")
        self.login()

    def login(self):
        self.wd.get("https://www.facebook.com/login")
        self.wd.find_element_by_id("email").send_keys(self.username)
        self.wd.find_element_by_id("pass").send_keys(self.password)
        self.wd.find_element_by_id("loginbutton").click()

    def convert_to_int(self,string):
        try:
            return int(string)
        except ValueError:
            if string.lower().endswith("k"):
                return int(float(string[:-2])*1000)

    def get_posts(self):
        articles = self.wd.find_elements_by_xpath("//*[@role='article'][not(@data-story_category)]")
        data = []
        for a in articles:
            if a.get_attribute("id").startswith("hyperfeed_story_id_"):
                likeIts = [i.get_attribute("aria-label").split() for i in a.find_elements_by_class_name("_3emk") if i.get_attribute("aria-label")]
                likes = {"Like":0,"Love":0,"Haha":0,"Wow":0,"Sad":0,"Angry":0}
                likes.update({i[1]: self.convert_to_int(i[0]) for i in likeIts})
                try:
                    button = a.find_element_by_class_name("UFILikeLink")
                except exceptions.NoSuchElementException:
                    continue
                data.append({"likes":likes,"button":button,"article":a})
        return data

    def scroll(self,page_end=100):
        find_elem = None
        scroll_from = 0
        scroll_limit = self.wd.execute_script("return document.body.scrollHeight")
        i = 0
        while not find_elem:
            self.wd.execute_script("window.scrollTo(%d, %d);" % (scroll_from, scroll_from + scroll_limit))
            scroll_from += scroll_limit
            i += 1
            if page_end and i >= page_end:
                break
            try:
                find_elem = self.wd.find_element_by_xpath("//span[@class='_38my']")
                find_elem.click()
            except exceptions.ElementNotVisibleException:
                find_elem = None
            except exceptions.NoSuchElementException:
                find_elem = None

    def automate(self,unlike=False,page_end=100):
        if self.status_report: print("Forcing Facebook to load the posts...")
        self.scroll(page_end)
        if self.status_report: print("Scrolled down %s times" % page_end)
        if self.status_report: print("%s posts..." % ("Unliking" if unlike else "Liking"))
        self.wd.execute_script("window.scrollTo(0,0);")
        posts = self.get_posts()
        num = 0
        for p in posts:
            if p["likes"]["Angry"] == 0 and p["likes"]["Sad"] == 0 and p["likes"]["Like"] >= 5:
                article = p["article"]
                self.wd.execute_script("arguments[0].scrollIntoView();", article)
                button = article.find_element_by_class_name("UFILikeLink")
                if button.get_attribute("aria-pressed") == ("true" if unlike else "false"):
                    num += 1
                    self.wd.execute_script("arguments[0].click();",button)
                    try:
                        p = article.find_element_by_tag_name("p").get_attribute("innerText").replace("\n"," ")
                    except exceptions.NoSuchElementException:
                        p = ""
                    if self.status_report: print('%s "%s"' % ("Unliked" if unlike else "Liked",p))
        if self.status_report: print("%s %s posts" % ("Unliked" if unlike else "Liked",num))

    def close(self):
        self.wd.close()


username = input("Username: ")
password = input("Password: ")

pages = False
while pages is False:
    inp = input("How many pages to go through? (default 100, 'all' for whole News Feed): ")
    if inp.isdigit():
        pages = int(inp)
    elif inp == "all":
        pages = None

unlike = None
while unlike is None:
    inp = input("Do you want to Like (l) or Unlike (u) posts? ")
    if inp == "l":
        unlike = False
    elif inp == "u":
        unlike = True

bot = FacebookBot(username,password,status_report=True)

bot.automate(unlike=unlike, page_end=pages)
print("Finished")
print()

input("Return to exit")
try:
    bot.close()
except:
    pass
