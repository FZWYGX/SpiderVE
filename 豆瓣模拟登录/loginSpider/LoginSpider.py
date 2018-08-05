from urllib.request import urlretrieve
import requests
from lxml import etree
import re
from base64 import b64encode
from settings import USERNAME, PASSWORD, APPCODE

import tesserocr
from PIL import Image


class DouBanLogin(object):
    def __init__(self):
        self.url = 'https://accounts.douban.com/login'
        self.headers = {
            'Host': 'accounts.douban.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }

        self.form_data = {
            "source": "None",
            "redir": "https://douban.com",
            "form_email": USERNAME,
            "form_password": PASSWORD,
            "remember": "on",
            "login": "登录"
        }

        self.session = requests.Session()

    def is_captcha(self, selector):
        """
        判断是否有验证码
        """
        # 判断是否有验证码
        captcha_url = selector.xpath("//img[@id='captcha_image']/@src")
        if captcha_url[0] is not None:
            captcha_url = captcha_url[0]

            # 这个是去调用阿里云市场 - 图谱按验证码识别
            # code = self.aliyun_captcha(captcha_url)

            # 这个代码通过tesserocr识别验证码, 不过成功率很低, 不推荐
            # code = self.ocr_captcha(captcha_url)

            # 这个代码是手动输入验证码
            code = self.hand_captcha(captcha_url)

            # 拿到'captcha-solution'
            self.form_data['captcha-solution'] = code
            # 拿到'captcha-id'
            captcha_id = selector.xpath("//input[@name='captcha-id']/@value")[0]
            self.form_data['captcha_id'] = captcha_id
        print(self.form_data)

    def hand_captcha(self, captcha_url):
        """
        手动输入验证码
        """
        urlretrieve(captcha_url, 'captcha.png')
        image = Image.open('captcha.png')
        image.show()
        code = input('请输入验证码:')
        return code

    def ocr_captcha(self, captcha_url):
        """
        tesserocr识别验证码, 不过识别程度一般
        """
        urlretrieve(captcha_url, 'captcha.png')
        image = Image.open('captcha.png')

        image = image.convert('L')
        threshold = 100
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)

        image = image.point(table, '1')
        image.show()

        code = tesserocr.image_to_text(image)

        return code

    def aliyun_captcha(self, captcha_url):
        """
        阿里云市场 - 图片验证码识别
        """
        # 下载图片
        urlretrieve(captcha_url, 'captcha.png')
        # 阿里云图片识别接口
        recognize_url = 'https://jisuyzmsb.market.alicloudapi.com/captcha/recognize?type=e'
        # 阿里云接口需要pic参数, 并且, 验证码图片base64加密格式
        body = {}
        with open('captcha.png', 'rb') as f:
            data = f.read()
            pic = b64encode(data)
            body['pic'] = pic

        appcode = APPCODE

        headers = {
            'Authorization': 'APPCODE ' + appcode,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

        response = requests.post(recognize_url, data=body, headers=headers)
        # 返回的内容是字典
        result = response.json()
        code = result['result']['code']
        print("通过阿里云识别的验证码为：", code)
        return code

    def login(self):
        response = self.session.get(self.url, headers=self.headers)
        selector = etree.HTML(response.text)

        # 判断是否有验证码
        self.is_captcha(selector)

        response = self.session.post(self.url, data=self.form_data, headers=self.headers)

        # 判断条件是您的用户名是否在网页中
        if response.status_code == 200:
            user_num = re.findall(USERNAME, response.text)
            if len(USERNAME) > 0 and len(user_num) > 0 and USERNAME == user_num[0]:
                print("找到了您的用户名：", user_num[0])
                print("登录成功")
            else:
                print("登录失败")
        else:
            print("response.status_code不是200")


if __name__ == '__main__':
    douban = DouBanLogin()
    douban.login()






