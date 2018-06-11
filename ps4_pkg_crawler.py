import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from retry import retry
import re


header_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"


@retry(exceptions=(requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout), delay=2, backoff=2,
       jitter=(0, 5), max_delay=30)
def get_content_in_detail_page(id):
    detail_page = requests.get("http://www.ksohu.com/post/{0}.html".format(id),
                               headers={"User-Agent": header_ua, "Cookie": 'commshow-{0}=1'.format(id)},
                               timeout=10).content
    detail_page = BeautifulSoup(detail_page, "lxml")
    content = detail_page.select('div.post div.post-body')[0]
    if content.find('a') is not None:
        a = content.find('a')
        a.string = a['href']
    return content.get_text().strip().replace('\r', ' ').replace('\n', ' ')


@retry(exceptions=(requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout), delay=2, backoff=2,
       jitter=(0, 5), max_delay=30)
def get_data(page, last_id=None):
    result = []
    request = requests.get("http://www.ksohu.com/page_{0}.html".format(page),
                           headers={"User-Agent": header_ua}, timeout=10)
    home_page = BeautifulSoup(request.content, "lxml")
    if request.status_code != 200:
        print('get page {0} err')
        print(home_page.prettify())
        return result

    post = home_page.select('div.article div.post')

    # id time title content info
    for p in post:
        if len(p.select('i.fa-arrow-circle-up')) > 0:  # 不处理置顶内容
            continue

        time = p.select('span.date')[0].get_text().strip()
        if len(time) == 11:  # 2018年06月05日
            time = '{0}-{1}-{2}'.format(time[:4], time[5:7], time[-3:-1])

        t = p.select('div.div-title')[0]
        url = t.find('a')['href']
        p_id = int(re.compile(r'(\d+)\.html').findall(url)[0])
        if last_id is not None and p_id <= last_id:
            break

        title = t.find('a').get_text().strip()

        content = p.find('div', class_='intro')
        if content is not None:
            content = content.get_text().strip().replace('\r', ' ').replace('\n', ' ')
            if content.__contains__('***请进入文章页查看隐藏内容***') or content.__contains__('请您放心下载'):
                content = get_content_in_detail_page(p_id)

        info = p.select('div.more span.readmore a')[0]
        if info is not None:
            info = info.get_text().strip()
        result += [p_id, time, title, content, info]
    return result


if __name__ == "__main__":
    data = []
    last_id = 361
    for p in range(1, 21):  # 1到20页
        new_page = get_data(p, last_id)
        if len(new_page) <= 0:
            break
        data += new_page
    if len(data) > 0:
        data = np.array(data)
        data = data.reshape((-1, 5))
        df = pd.DataFrame(data, columns=['id', 'time', 'title', 'content', 'info'], index='id')
        print(df.head())
        df.to_csv('ps4_pkg_({0}-{1}].csv'.format(last_id, df.iloc[0]['id']))
    # print(get_content_in_detail_page(138))
