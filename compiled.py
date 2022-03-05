import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import json


def init_chromedriver(url):
    options = uc.ChromeOptions()
    options.headless = False
    # options.user_data_dir = "/home/jxt1n/.config/chromium/"
    driver = uc.Chrome(options=options)
    driver.get(url)
    return driver


def load_json(filename):
    with open(filename, "r") as json_file:
        return json.load(json_file)


def dump_json(filename, data):
    with open(filename, "w") as json_file:
        json.dump(data, json_file)


def click_see_more_friends():
    global driver
    driver.find_element_by_id("m_more_friends").find_element_by_tag_name("a").click()


def scrape_cur_page():
    global driver
    global friend2url
    tags = driver.find_elements_by_tag_name("tbody")
    for tag in tags[1:-2]:
        data = tag.find_element_by_tag_name("a")
        name = data.text
        profile_link = data.get_attribute("href")
        print(data.text)
        print(data.get_attribute("href"))
        if "hovercard" in profile_link:
            continue
        profile_link = profile_link.split("fref=fr_tab")[0][:-1]
        friend2url[name] = profile_link


# code block to scrape all complete friend_list
def generate_friend2url():
    pg_count = 1
    while True:
        print(pg_count)
        scrape_cur_page()
        try:
            click_see_more_friends()
            pg_count += 1
        except Exception as e:
            print("Reached End")
            del friend2url["Find Friends"]
            dump_json("friend2url.json", friend2url)
            break


def break_to_feel_real():  # not sure if needed anymore
    global driver
    driver.get("https://www.jxtin.me")
    time.sleep(3)


def get_BirthDate_old(profile_url):  # can be used
    global driver
    friend2url = load_json("friend2url.json")
    profile_url = profile_url.replace("mbasic", "www")
    if "?id=" in profile_url:
        driver.get(profile_url + "&sk=about_contact_and_basic_info")
    else:
        driver.get(profile_url + "/about_contact_and_basic_info")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    year_str = soup.find_all("div", string="Birth year")
    date_str = soup.find_all("div", string="Birth date")
    if date_str:  # need to include partial cases by changing and to or
        print("DOB-Exists")
        bday = date_str[0].find_parent().text.split("B")[0]
        print(bday)
        return bday
    else:
        print("DOB no exist")


def generate_friend2bday_old():  # yes use this
    count = 0
    friend2bday = {}
    for friend, url in list(friend2url.items())[:]:
        count += 1
        bday = get_BirthDate_old(url)
        time.sleep(0.5)
        if bday is not None:
            print("should append")
            friend2bday[friend] = bday
            print(friend2bday)
        if count % 30 == 0:
            break_to_feel_real()

    print(friend2bday)
    print("Do you want to save the data? (y/n)")
    if input() == "y":
        dump_json("friend2bday.json", friend2bday)


if __name__ == "__main__":
    driver = init_chromedriver()
    print("Login to Facebook")
    driver.get("https://www.facebook.com/")
    if input("Done?") == "y":
        generate_friend2url()
        generate_friend2bday_old()
        driver.close()
