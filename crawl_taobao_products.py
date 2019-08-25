
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as pq
import pymongo
import time


browser = webdriver.Firefox()
wait = WebDriverWait(browser, 10)
MONGO_URL = 'localhost'
MONGO_DB = 'taobao'
MONGO_COLLECTION = 'products'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
MAX_PAGE = 20


def index_page(page):
    """
    抓取索引页
    :param page: 页码
    """
    time.sleep(3)
    print('-----------------------------------------------------')
    print('--------------正在爬取第', page, '页--------------------')
    print('-----------------------------------------------------')
    get_products()
    try:
        url = 'https://uland.taobao.com/sem/tbsearch?refpid=mm_26632360_8858797_29866178&clk1=a79d63827761d7181773d3a3ece5498d&keyword=iPad&page='\
              + str(page)
        browser.get(url)
        if page > 1:
            nextPage = wait.until(EC.presence_of_element_located((By.ID, 'Jumper')))
            submit = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'pageConfirm')))
            nextPage.clear()
            nextPage.send_keys(page)
            submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'), str(page)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.searchResult.ItemWrapper.item')))

    except TimeoutException:
        print("失败")
        # index_page(page)


def get_products():
    """
    提取商品数据
    """
    html = browser.page_source
    doc = pq(html)
    items = doc('#searchResult #ItemWrapper .item').items()
    for item in items:
        print(item.text())
        product = {
            'image': 'https://'+item.find('.imgContainer .imgLink img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.payNum').text(),
            'title': item.find('.title').text(),
            'shop': item.find('.shopNick').text(),
        }
        print(product)
        save_to_mongo(product)


def save_to_mongo(result):
    """
    保存至MongoDB
    :param result:结果
    """
    try:
        if db[MONGO_COLLECTION].insert(result):
            print('存储到MongoDB成功')
    except Exception:
        print('存储到MongoDB失败')


def main():
    """
    遍历每一页
    """
    for page in range(1, MAX_PAGE+1):
        index_page(page)


if __name__ == '__main__':
    main()
