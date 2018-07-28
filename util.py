import requests
import pandas as pd
import re
import glob


header_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"


def check_link(id, content):
    content = str(content)
    pattern = re.compile(r'1([A-Za-z0-9_-]{22})|(?<=pan.baidu.com/s/)1([A-Za-z0-9_-]{7})')  # 匹配新版22位或老版7位
    if pattern.search(content):
        surl = pattern.findall(content)[0]
        pattern = re.compile(r'(?<!解压)密码\W*\s*([A-Za-z0-9]{4})')  # 反向否定匹配

        # check页面存在
        resp = requests.get('https://pan.baidu.com/s/1{0}'.format(surl),
                            headers={'Host': 'pan.baidu.com', "User-Agent": header_ua}, timeout=30)
        if resp.status_code == 404 or '百度网盘-链接不存在' in resp.content.decode():
            print('check {0} err: url [1{1}] not exist.'.format(id, surl))
            return False

        # check密码正确
        if pattern.search(content):
            pwd = pattern.findall(content)[0]
            result = requests.post('http://pan.baidu.com/share/verify',
                                   params={'surl': surl},
                                   data={'pwd': pwd},
                                   headers={'Referer': 'http://www.baidu.com', "User-Agent": header_ua}).json()
            if result['errno'] == 0 and result['randsk'] is not None:
                return True
            else:
                print('check {0} err: url [1{1}], pwd [{2}], result {3}.'.format(id, surl, pwd, result))
                return False
        else:
            return True
    else:
        print("no url for id {0}".format(id))
        return False


def update_content(id, content):
    print('go through...{0}'.format(id))
    import ps4_pkg_crawler
    if check_link(id, content):
        return content
    else:
        new_content = ps4_pkg_crawler.get_content_in_detail_page(id)
        print('{0} has been updated!'.format(id))
        return new_content if new_content is not None else "【页面失效了】"


if __name__ == '__main__':
    # check available
    csv = 'ps4_pkg_(0-465].csv'
    df = pd.read_csv(csv)
    df['content'] = df.apply(lambda x: update_content(x['id'], x['content']), axis=1)
    df.to_csv(csv, index=False)

    # merge csv
    # print(glob.glob("*.csv"))
    # print(sorted(glob.glob("*.csv"), key=lambda s: s[-s.rfind('('):s.rfind(']')], reverse=True))
    # df = pd.concat([pd.read_csv(csv) for csv in sorted(glob.glob("*.csv"), key=lambda s: s[-s.rfind('('):s.rfind(']')], reverse=True)], axis=0)
    # df.to_csv('ps4_pkg_(0-465].csv', index=False, columns=['id', 'time', 'title', 'content', 'info'])

