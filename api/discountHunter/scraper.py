import re
import requests
from bs4 import BeautifulSoup
from .categories import kaufland_cats, billa_cats, lidl_cats
from datetime import datetime, timedelta
from products.models import Promotion, Product

BILLA_LOGO = "https://d1yjjnpx0p53s8.cloudfront.net/styles/logo-thumbnail/s3/0012/8033/brand.gif?itok=zP8_dFEh"


def convert_to_date(date_text):
    if (int(date_text.split('.')[1])) < datetime.now().month - 1:
        year = datetime.now().year + 1
    else:
        year = datetime.now().year

    date_text = datetime.strptime(f"{date_text}{year} 00:00:00", "%d.%m.%Y %H:%M:%S")
    return date_text


def get_product_discount_phrase(soup, class_name):
    try:
        product_discount_phrase = soup.select_one(class_name).text.strip()
    except AttributeError:
        product_discount_phrase = None

    return product_discount_phrase


def get_product_title(soup, class_name):
    try:
        product_title = soup.select_one(class_name).text.strip()
    except AttributeError:
        product_title = None

    return product_title


def get_product_new_price(soup, class_name):
    try:
        product_new_price = float(soup.select_one(class_name).text.strip().replace(",", "."))
    except AttributeError:
        product_new_price = None

    return product_new_price


def get_product_quantity(soup, class_name):
    try:
        product_quantity = soup.select_one(class_name).text.strip()
    except AttributeError:
        product_quantity = None

    return product_quantity


def get_billa_promotion_start_date(soup):
    promotion_text = soup.find("div", 'date').get_text().split(" ")
    try:
        promotion_starts = datetime.strptime(promotion_text[-5], '%d.%m.%Y')
    except AttributeError:
        promotion_starts = None

    return promotion_starts


def get_billa_promotion_expire_date(soup):
    promotion_text = soup.find("div", 'date').get_text().split(" ")
    try:
        promotion_expires = datetime.strptime(promotion_text[-2], '%d.%m.%Y')
    except AttributeError:
        promotion_expires = None

    return promotion_expires


def get_billa_product_new_price(soup, class_name):
    product_prices = soup.select(class_name)
    product_new_price = None
    if len(product_prices) == 2:
        product_new_price = float(product_prices[1].text.strip())
    elif len(product_prices) == 1:
        product_new_price = float(product_prices[0].text.strip())

    return product_new_price


def get_billa_product_old_price(soup, class_name):
    product_prices = soup.select(class_name)
    product_old_price = None
    if len(product_prices) == 2:
        product_old_price = float(product_prices[0].text.strip())

    return product_old_price


def get_kaufland_product_old_price(soup, class_name):
    try:
        product_old_price = float(soup.select_one(class_name).text.strip().replace(",", "."))
    except ValueError or AttributeError:
        product_old_price = None

    return product_old_price


def get_kaufland_product_base_price(soup, class_name):
    try:
        product_base_price = soup.select_one(class_name).text.strip()
    except AttributeError:
        product_base_price = None

    return product_base_price


def get_kaufland_product_promotion_message(soup, class_name1, class_name_2):
    try:
        promotion_message = soup.select_one(class_name1).text.strip()
    except AttributeError:
        try:
            promotion_message = soup.select_one(class_name_2).text.strip()
        except AttributeError:
            promotion_message = None

    return promotion_message


def get_kaufland_product_sub_title(soup, class_name):
    try:
        product_subtitle = soup.select_one(class_name).text.strip()
    except AttributeError:
        product_subtitle = None

    return product_subtitle


def get_kaufland_product_discount_phrase(soup, class_name1, class_name2):
    try:
        product_discount_phrase = soup.select_one(class_name1).text.strip()
    except AttributeError:
        try:
            float(soup.select_one(class_name2).text.strip().replace(",", "."))
            product_discount_phrase = None
        except ValueError:
            product_discount_phrase = soup.select_one(class_name2).text.strip()

    return product_discount_phrase


def get_kaufland_promotion_text(soup, class_name):
    try:
        promotion_text = soup.find("div", class_name).find("span").text.strip()
    except AttributeError:
        promotion_text = None

    return promotion_text


def get_kaufland_product_image_url(soup, class_name):
    try:
        product_image_url = soup.find("img", class_name)['src']
    except AttributeError:
        product_image_url = None

    return product_image_url


def get_kaufland_product_description(soup, class_name):
    try:
        description_wrapper = str(soup.select_one(class_name).find("p"))
        description_wrapper = description_wrapper.replace("<br/>", '\n')
        description_list = []
        for line in description_wrapper.split('\n'):
            if not "p>" in line:
                description_list.append(line.strip())
        product_description = "\n".join(description_list)
    except AttributeError:
        product_description = None

    return product_description


def get_lidl_product_old_price(soup, class_name):
    try:
        product_old_price = soup.select_one(class_name).find(
            "span").text.strip()
    except AttributeError:
        product_old_price = None
    else:
        try:
            product_old_price = float(product_old_price.replace(",", "."))
        except ValueError:
            product_old_price = None

    return product_old_price


def get_lidl_product_description(soup, class_name):
    try:
        product_description = "\n".join([description.text for description in
                                         soup.select_one(class_name).find_all("li")])
    except AttributeError:
        product_description = None

    return product_description


def get_lidl_product_promotion_interval(soup, class_name):
    try:
        promotion_interval = soup.select_one(class_name).text.strip()
        promotion_starts = promotion_interval.split()[-3]
        if promotion_starts == 'само':
            promotion_starts = None
        promotion_expires = promotion_interval.split()[-1]
    except AttributeError:
        promotion_starts = None
        promotion_expires = None
    except IndexError:
        promotion_starts = promotion_interval.split()[-1]
        promotion_expires = convert_to_date(promotion_interval.split()[-1]) + timedelta(days=7)

    if promotion_starts:
        promotion_starts = convert_to_date(promotion_starts)
    if promotion_expires and not type(promotion_expires) == datetime:
        promotion_expires = convert_to_date(promotion_expires)

    return promotion_starts, promotion_expires


def get_lidl_product_image_url(soup, class_name):
    try:
        product_image_url = soup.find("a", class_name)["href"]
    except AttributeError:
        product_image_url = None

    return product_image_url


def billa(store):
    response = requests.get(billa_cats[0])
    if response.status_code != 200:
        return False

    soup = BeautifulSoup(response.text, "html.parser")
    promotion_starts = get_billa_promotion_start_date(soup)
    promotion_expires = get_billa_promotion_expire_date(soup)
    promotion, _ = Promotion.objects.get_or_create(store=store, expire_date=promotion_expires,
                                                   start_date=promotion_starts)

    products = soup.find_all("div", 'product')
    for product in products:
        product_title = get_product_title(product, ".actualProduct")
        product_old_price = get_billa_product_old_price(product, ".price")
        product_new_price = get_billa_product_new_price(product, ".price")
        product_discount_phrase = get_product_discount_phrase(product, ".discount")

        if product_new_price:
            product, _ = Product.objects.get_or_create(promotion=promotion, title=product_title,
                                                       old_price=product_old_price, new_price=product_new_price,
                                                       discount_phrase=product_discount_phrase,
                                                       image_url=BILLA_LOGO
                                                       )
    return True


def get_kaufland_category_products_url(category):
    response = requests.get(category)
    if response.status_code != 200:
        return False

    soup = BeautifulSoup(response.text, "html.parser")
    products = soup.find_all("a", ["m-offer-tile__link", "u-button--hover-children"])
    category_products_urls = [f"https://www.kaufland.bg{product['href']}" for product in products if
                              product['target'] == "_self"]
    return category_products_urls


def kaufland(store):
    for category in kaufland_cats[:]:
        products = get_kaufland_category_products_url(category)
        for product in products:
            response = requests.get(product)
            if response.status_code != 200:
                return False

            soup = BeautifulSoup(response.text, "html.parser")
            product_image_url_wrapper = get_kaufland_product_image_url(soup, ["a-image-responsive",
                                                                              "a-image-responsive--preview-knockout"])
            resize_index = product_image_url_wrapper.find("?MYRAVRESIZE")
            if resize_index != -1:
                product_image_url = product_image_url_wrapper[:resize_index]
            else:
                product_image_url = product_image_url_wrapper

            promotion_text = get_kaufland_promotion_text(soup, ["a-eye-catcher", "a-eye-catcher--secondary"])
            if promotion_text:
                promotion_starts = convert_to_date(promotion_text.split()[-3])
                promotion_expires = convert_to_date(promotion_text.split()[-1])
            else:
                promotion_starts = None
                promotion_expires = None

            product_subtitle = get_kaufland_product_sub_title(soup, ".t-offer-detail__subtitle")
            product_title = get_product_title(soup, ".t-offer-detail__title")
            product_discount_phrase = get_kaufland_product_discount_phrase(soup, ".a-pricetag__discount",
                                                                           ".a-pricetag__old-price")
            product_old_price = get_kaufland_product_old_price(soup, ".a-pricetag__old-price")

            product_new_price = get_product_new_price(soup, ".a-pricetag__price")
            product_base_price = get_kaufland_product_base_price(soup, ".t-offer-detail__basic-price")
            product_quantity = get_product_quantity(soup, ".t-offer-detail__quantity")
            product_description = get_kaufland_product_description(soup, ".t-offer-detail__description")

            promotion_message = get_kaufland_product_promotion_message(soup, ".t-offer-detail__mpa",
                                                                       ".t-offer-detail__promo-message")

            promotion, _ = Promotion.objects.get_or_create(store=store, expire_date=promotion_expires,
                                                           start_date=promotion_starts)

            product, _ = Product.objects.get_or_create(promotion=promotion, title=product_title,
                                                       sub_title=product_subtitle,
                                                       old_price=product_old_price, new_price=product_new_price,
                                                       base_price=product_base_price, quantity=product_quantity,
                                                       discount_phrase=product_discount_phrase,
                                                       description=product_description,
                                                       image_url=product_image_url, promo_message=promotion_message
                                                       )
    return True


def get_lidl_category_products_url(category):
    response = requests.get(category)
    if response.status_code != 200:
        return False

    soup = BeautifulSoup(response.text, "html.parser")
    products = soup.find_all("a", "ret-o-card__link nuc-a-anchor")
    category_products_urls = [f"https://www.lidl.bg/{product['href']}" for product in products]
    return category_products_urls


def lidl(store):
    for category in lidl_cats[:]:
        products = get_lidl_category_products_url(category)
        for product in products:
            response = requests.get(product)
            if response.status_code != 200:
                return False

            soup = BeautifulSoup(response.text, "html.parser")
            product_component = soup.select_one(".attributebox")
            product_image_url = get_lidl_product_image_url(soup, "multimediabox__preview-link")
            product_title = " ".join(
                re.sub('\n', '', get_product_title(product_component, ".attributebox__headline--h1")).split())

            # Shows discount % as well as other type of promotion 'СПЕСТИ 20 ЛВ. САМО НА 05.11.'
            product_discount_phrase = get_product_discount_phrase(product_component, ".pricebox__highlight")
            product_old_price = get_lidl_product_old_price(product_component, ".pricebox__recommended-retail-price")
            product_new_price = get_product_new_price(product_component, ".pricebox__price")
            product_quantity = get_product_quantity(product_component, ".pricebox__basic-quantity")
            product_description = get_lidl_product_description(product_component, ".textbody")

            # Promotion could be interval date-date, but could be 'само на date', 'от date'
            # if promotion_starts is None - 'само на date'
            promotion_starts, promotion_expires = get_lidl_product_promotion_interval(product_component,
                                                                                      ".ribbon__text")

            promotion, _ = Promotion.objects.get_or_create(store=store, expire_date=promotion_expires,
                                                           start_date=promotion_starts)

            product, _ = Product.objects.get_or_create(promotion=promotion, title=product_title,
                                                       old_price=product_old_price, new_price=product_new_price,
                                                       quantity=product_quantity,
                                                       discount_phrase=product_discount_phrase,
                                                       description=product_description,
                                                       image_url=product_image_url
                                                       )
    return True
