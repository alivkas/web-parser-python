import requests
from bs4 import BeautifulSoup

response_main = requests.get('https://ekb.hi-stores.ru/catalog/smartphones/')
soup_main = BeautifulSoup(response_main.content, "lxml")

first_page = soup_main.find("div", class_="top_wrapper items_wrapper catalog_block_template")
elements = first_page.find_all(attrs={'data-id': True})

id_set = set()
for product_id in elements:
    data_id = product_id['data-id']
    id_set.add(data_id)

for product in id_set:
    product_page = first_page.find(attrs={'data-id': product})
    product_title = product_page.find("a", class_="dark_link js-notice-block__title option-font-bold font_sm")
    print(product_title.get_text())

nums_div = soup_main.find("div", class_="nums")
nums = nums_div.find_all("a", class_="dark_link")
last_page = nums[len(nums) - 1].text

# TODO
id_set2 = set()
for i in range(2, int(last_page) + 1):
    response_catalog = requests.get(f'https://ekb.hi-stores.ru/catalog/smartphones/?PAGEN_1={i}')
    soup_catalog = BeautifulSoup(response_catalog.content, "lxml")
    catalog = soup_catalog.find("div", class_="top_wrapper items_wrapper catalog_block_template")
    elements_catalog = catalog.find_all(attrs={'data-id': True})

    for product_id in elements_catalog:
        data_id = product_id['data-id']
        id_set2.add(data_id)

    for product in id_set2:
        product_page = catalog.find(attrs={'data-id': product})
        product_title = product_page.find("a", class_="dark_link js-notice-block__title option-font-bold font_sm")
        print(product_title.get_text())
