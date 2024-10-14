import requests
from bs4 import BeautifulSoup

# Метод для парсинга первой страницы и остальных
def parse_url(url, page_num, title_price):
    response_catalog = ""
    if "?PAGEN_1=" in url:
        response_catalog = requests.get(f'https://ekb.hi-stores.ru/catalog/smartphones/?PAGEN_1={page_num}')
    else:
        response_catalog = requests.get(f'https://ekb.hi-stores.ru/catalog/smartphones/')

    soup_catalog = BeautifulSoup(response_catalog.content, "lxml")
    catalog = soup_catalog.find("div", class_="top_wrapper items_wrapper catalog_block_template")
    elements_catalog = catalog.find_all(attrs={'data-id': True}) # Получение id всех товаров

    id_set = set() # Для устранения дубликатов id при парсинге
    for product_id in elements_catalog:
        data_id = product_id['data-id']
        id_set.add(data_id)
    id_list = list(id_set) # Для более быстрой итерации

    for product in id_list:
        product_page = catalog.find(attrs={'data-id': product})
        product_title = product_page.find("a", class_="dark_link js-notice-block__title option-font-bold font_sm")
        product_price = product_page.find("span", class_="price_value")
        title_price[product_title.get_text()] = product_price.get_text()

    id_set.clear()

    return title_price

# Получение контента для пагинации
response_main = requests.get('https://ekb.hi-stores.ru/catalog/smartphones/')
soup_main = BeautifulSoup(response_main.content, "lxml")
title_price = {}

parse_url(url="https://ekb.hi-stores.ru/catalog/smartphones/", page_num=0, title_price=title_price)

# Нахождение последней страницы, для прохода по всем кроме первой
nums_div = soup_main.find("div", class_="nums")
nums = nums_div.find_all("a", class_="dark_link")
last_page = nums[len(nums) - 1].text

# Проход по всем страницам
for i in range(2, int(last_page) + 1):
    parse_url(url="https://ekb.hi-stores.ru/catalog/smartphones/?PAGEN_1=", page_num=i, title_price=title_price)

print(title_price)
