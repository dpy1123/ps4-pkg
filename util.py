import requests
import pandas as pd
import re
import glob


header_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"


def check_link(id, content):
    content = str(content)
    pattern = re.compile(r'[a-zA-z]+://pan.baidu.com/s/1([A-Za-z0-9_-]*)')
    if pattern.search(content):
        surl = pattern.findall(content)[0]
        pattern = re.compile(r'密码\W*\s*([A-Za-z0-9]{4})')
        if pattern.search(content):
            pwd = pattern.findall(content)[0]
            result = requests.post('http://pan.baidu.com/share/verify',
                                   params={'surl': surl},
                                   data={'pwd': pwd},
                                   headers={'Referer': 'http://www.baidu.com', "User-Agent": header_ua}).json()
            if result['errno'] == 0 and result['randsk'] is not None:
                return True, result
            else:
                print(id, surl, pwd, result)
                return False
        else:
            resp = requests.get('https://pan.baidu.com/s/1{0}'.format(surl),
                                headers={'Host': 'pan.baidu.com', "User-Agent": header_ua}, timeout=10)
            if resp.status_code == 404:
                print(id, surl)
                return False
            else:
                return True, resp.content.decode()
    else:
        print("no url for id {0}".format(id))


if __name__ == '__main__':
    # check available
    # csv = 'ps4_pkg_(0-336].csv'
    # df = pd.read_csv(csv, index_col=0)
    # df['available'] = df.apply(lambda x: check_link(x['id'], x['content']), axis=1)
    # print(df.head())
    # df.to_csv(csv)

    # merge csv
    df = pd.concat([pd.read_csv(csv) for csv in glob.glob("*.csv")], axis=0)
    print(df.tail())
    df.to_csv('ps4_pkg_(0-440].csv', index=False, columns=['id', 'time', 'title', 'content', 'info'])

