# -*- coding: utf-8 -*-
import scrapy
import re
from urllib.request import urlretrieve
from base64 import b64encode
import requests
from PIL import Image
import tesserocr
from ..settings import USERNAME, PASSWORD, APPCODE


class LoginSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['douban.com']
    start_urls = ['https://accounts.douban.com/login']

    login_url = 'https://accounts.douban.com/login'

    def parse(self, response):
        form_data = {
            "source": "None",
            "redir": "https://douban.com",
            "form_email": USERNAME,
            "form_password": PASSWORD,
            "remember": "on",
            "login": "登录"
        }

        # 判断是否有验证码
        captcha_url = response.xpath("//img[@id='captcha_image']/@src").extract_first()
        if captcha_url:

            # 这个是去调用阿里云市场 - 图谱按验证码识别
            # code = self.aliyun_captcha(captcha_url)

            # 这个代码通过tesserocr识别验证码, 不过成功率很低, 不推荐
            # code = self.ocr_captcha(captcha_url)

            # 这个代码是手动输入验证码
            code = self.hand_captcha(captcha_url)

            # 拿到'captcha-solution'
            form_data['captcha-solution'] = code
            # 拿到'captcha-id'
            captcha_id = response.xpath("//input[@name='captcha-id']/@value").extract_first()
            form_data['captcha_id'] = captcha_id

        yield scrapy.FormRequest(url=self.login_url, formdata=form_data,
                                 callback=self.parse_after_login)

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

    def parse_after_login(self, response):
        user_num = re.findall(USERNAME, response.text)
        if len(USERNAME) > 0 and len(user_num) > 0 and USERNAME == user_num[0]:
            print("找到了您的用户名：", user_num[0])
            print("登录成功")
        else:
            print("登录失败")
