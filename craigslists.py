# Libraries
from bs4 import BeautifulSoup as bs  # pip install bs4
import requests  # pip install requests
import pandas as pd  # pip install pandas
import os
import time
from selenium import webdriver  # pip install selenium
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException


# Gets area and searches the item asked for
def item_search():
    global driver, item
    area = input('What area are you looking you\'re looking the product from (ex: new york, boston, miami)? ').lower()
    if ' ' in area:
        area = area.replace(' ', '')

    loop = True
    while loop:
        item = input('what do you want to search for? ')
        if item in characters:
            print(f"{characters} are invalid inputs.")
            continue
        break

    driver.get(f'https://{area}.craigslist.org/search/sss?')

    search = driver.find_element_by_xpath('//*[@id="query"]')
    search.send_keys(item)
    search.send_keys(Keys.RETURN)


# Get's the next page
def next_page():
    next = driver.find_element_by_xpath('//*[@id="searchform"]/div[3]/div[3]/span[2]/a[3]')
    next.click()


# Get's content of each item
def get_content():
    response = requests.get(driver.current_url)
    page = response.text

    soup = bs(page, 'html.parser')

    products = soup.find_all('li', {'class': 'result-row'})

    for product in products:
        data_dict = {}
        os.chdir(main_directory)
        data_dict['title'] = product.find('a', {'class': 'result-title hdrlnk'}).text
        data_dict['day_posted'] = product.find('time', {'class': 'result-date'}).text
        data_dict['link'] = product.find('a', {'class': 'result-title hdrlnk'})['href']
        meta = product.find('span', {'class': 'result-meta'}).find_all('span')
        data_dict['price'] = meta[0].text
        data_dict['location'] = meta[1].text

        for character in characters:
            if character in data_dict['title']:
                data_dict['title'] = data_dict['title'].replace(character, '')

        product_url = requests.get(data_dict['link'])
        product_page = product_url.text 
        product_soup = bs(product_page, 'html.parser')

        try:
            os.mkdir('products')
        except FileExistsError:
            pass

        prod_folder = main_directory + '\\' + 'products'
        os.chdir(prod_folder)

        pictures = product_soup.find_all('a', {'class': 'thumb'})
        try:
            os.mkdir(item)
        except FileExistsError:
            pass

        item_folder = prod_folder + '\\' + item
        os.chdir(item_folder)

        try:
            os.mkdir(data_dict['title'])

        except FileExistsError:
            pass

        time.sleep(.2)

        os.chdir(item_folder + "\\" + data_dict['title'])

        for picture in pictures:
            pic_url = picture['href']
            r = requests.get(pic_url)
            filename = pic_url.split('/')[-1]
            open(filename, 'wb').write(r.content)

        with open('product.txt', 'w') as file:
            file.write(data_dict['link'])
            file.write('\n' + data_dict['price'])

        if product_soup.find('p', {'class': 'attrgroup'}) is not None:

            attributes = product_soup.find_all('p', {'class': 'attrgroup'})[-1].text

            with open('product.txt', 'a') as file:
                file.write('\n\n' + attributes)

            att_text = open('product.txt', 'r')

            lines = att_text.readlines()
            
            for line in lines:
                line = line.strip()
                if 'fuel:' in line:
                    data_dict['fuel'] = line.split(" ")[-1]

                if 'odometer:' in line:
                    data_dict['odometer'] = line.split(" ")[-1]

                if 'title status:' in line:
                    data_dict['title_status'] = line.split(" ")[-1]

                if 'transmission:' in line:
                    data_dict['transmission'] = line.split(" ")[-1]

                if 'type:' in line:
                    data_dict['type'] = line.split(" ")[-1]

                if 'size:' in line:
                    data_dict['size'] = line.split(" ")[-1]

                if 'make / manufacturer:' in line:
                    data_dict['make / manufacturer'] = line.split(":")[-1]

                if 'model name / number:' in line:
                    data_dict['model name / number'] = line.split(":")[-1]

                if 'condition:' in line:
                    data_dict['condition'] = line.split(":")[-1]

        lists.append(data_dict)


if __name__ == '__main__':
    print(os.getcwd())
    characters = {'/', '\\', '%', '*', '"', '<', '>', '|', ':', '?'}

    path = os.getcwd() + "\\webdriver\\chromedriver.exe"

    main_directory = os.getcwd()

    driver = webdriver.Chrome(path)

    lists = []

    item_search()

    while True:
        try:
            a = 1
            get_content()
            print('page ' + str(a) + ' finished')
            next_page()
            a += 1

        except ElementNotInteractableException:
            print('Closing browser.')
            time.sleep(.5)
            driver.quit()
            break

    df = pd.DataFrame(lists)
    os.chdir(main_directory)
    df.to_csv(f'{item}.csv', index=False)
