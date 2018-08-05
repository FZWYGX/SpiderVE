# -*- coding: utf-8 -*-
import scrapy
import re
from traceback import format_exc
from ..settings import USERNAME, PASSWORD, USER


class Login01Spider(scrapy.Spider):
    name = 'login02'
    allowed_domains = ['github.com']
    start_urls = ['https://github.com/login']

    def parse(self, response):
        print(response.url)
        yield scrapy.FormRequest.from_response(
            response,  # 自动的从response中寻找from表单
            formdata={"login": USERNAME, "password": PASSWORD},
            callback=self.after_login
        )

    def after_login(self, response):
        user_num = re.findall(USER, response.text)
        if len(USER) > 0 and len(user_num) > 0 and USER == user_num[0]:
            print("找到了您的用户名：", user_num[0])
            print("登录成功")
        else:
            print("登录失败")

    def error_back(self, e):
        """
        报错机制
        """
        self.logger.error(format_exc())

