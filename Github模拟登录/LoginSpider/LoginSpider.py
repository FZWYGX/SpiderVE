import requests
import re
from lxml import etree
from settings import USERNAME, PASSWORD, USER


class GithubLogin(object):
    def __init__(self):
        self.headers = {
            'Referer': 'https://github.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Host': 'github.com'
        }
        # 登录地址
        self.login_url = 'https://github.com/login'
        # 模拟登录发起请求地址
        self.post_url = 'https://github.com/session'
        self.session = requests.Session()

    def token(self):
        response = self.session.get(self.login_url, headers=self.headers)
        selector = etree.HTML(response.text)

        # 在网页中拿到登录所需的一些data
        authenticity_token = selector.xpath("//input[@name='authenticity_token']/@value")[0]
        utf8 = selector.xpath("//input[@name='utf8']/@value")[0]
        commit = selector.xpath("//input[@name='commit']/@value")[0]

        post_data = dict(authenticity_token=authenticity_token,
                         utf8=utf8,
                         commit=commit)
        print(post_data)
        return post_data

    def login(self, username, password, user):
        data = {
            'login': username,
            'password': password
        }
        post_data = self.token()
        # 组成完整的data
        post_data.update(data)

        # 模拟登录
        response = self.session.post(self.post_url, data=post_data, headers=self.headers)

        # 验证条件是是否出现了您的用户名
        if response.status_code == 200:
            user_num = re.findall(user, response.text)
            if len(user) > 0 and len(user_num) > 0 and USER == user_num[0]:
                print("找到了您的用户名：", user_num[0])
                print("登录成功")
            else:
                print("登录失败")
        else:
            print("response.status_code不是200")


if __name__ == "__main__":
    login = GithubLogin()
    login.login(username=USERNAME,
                password=PASSWORD,
                user=USER)
