import requests
from bs4 import BeautifulSoup


def parse_url(page_num, title_price):
    url_to_fetch = f'https://ekb.hi-stores.ru/catalog/smartphones/'
    if page_num > 1:
        url_to_fetch += f'?PAGEN_1={page_num}'

    try:
        response_catalog = requests.get(url_to_fetch)
        response_catalog.raise_for_status()
        soup_catalog = BeautifulSoup(response_catalog.content, "lxml")
        catalog = soup_catalog.find("div", class_="top_wrapper items_wrapper catalog_block_template")

        if catalog is None:
            print(f"Warning: 'catalog' element not found on page {page_num}. Skipping...")
            return title_price

        elements_catalog = catalog.find_all(attrs={'data-id': True})

        for product_id_element in elements_catalog:
            product_id = product_id_element['data-id']
            product_page = catalog.find(attrs={'data-id': product_id})

            if product_page:
                product_title = product_page.find("a", class_="dark_link js-notice-block__title option-font-bold font_sm")
                product_price = product_page.find("span", class_="values_wrapper")

                if product_title and product_price:
                    title_price[product_title.get_text(strip=True)] = product_price.get_text(strip=True)
                else:
                    continue
            else:
                continue

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page_num}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred on page {page_num}: {e}")


    return title_price


def get_prices():
    response_main = requests.get('https://ekb.hi-stores.ru/catalog/smartphones/')
    soup_main = BeautifulSoup(response_main.content, "lxml")
    title_price = {}
    nums_div = soup_main.find("div", class_="nums")
    if nums_div:
        nums = nums_div.find_all("a", class_="dark_link")
        last_page = nums[-1].text if nums else 1
    else:
        last_page = 1
    for i in range(1, int(last_page) + 1):
        title_price = parse_url(page_num=i, title_price=title_price)
    return title_price