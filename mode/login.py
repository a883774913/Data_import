import random

import requests


class Login:
    def login(self):
        sess = requests.session()
        ran_13 = random.randint(1111111111111, 9999999999999)
        ran_10 = random.randint(111111111, 9999999999)
        url1 = f"http://18.118.13.94:80/jeecg-boot/sys/randomImage/{ran_13}?_t={ran_10}"
        sess.get(url=url1)

        URL = "http://18.118.13.94:80/jeecg-boot/sys/login"
        header = {'Connection': 'keep-alive',
                  'Content-Length': '103',
                  'Accept': 'application/json,text/plain,*/*',
                  'tenant-id': '0',
                  'User-Agent': 'Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,'
                                'likeGecko)Chrome/98.0.4758.80Safari/537.36Edg/98.0.1108.43',
                  'Content-Type': 'application/json',
                  'Accept-Encoding': 'gzip,deflate',
                  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}
        data = f'{{"username":"test","password":"Xx.888888","captcha":"0000","checkKey":"{ran_13}","remember_me' \
               f'":"true"}} '
        res = sess.post(url=URL, data=data, headers=header)
        token = res.json()['result']['token']
        return sess, token

if __name__ == '__main__':
    a = Login()
    a.login()