# -*- coding: utf-8 -*-
import scrapy
import re
from traceback import format_exc
from ..settings import USERNAME, PASSWORD, USER


class Login01Spider(scrapy.Spider):
    name = 'login01'
    allowed_domains = ['github.com']
    start_urls = ['https://github.com/login']

    def parse(self, response):
        print(response.url)
        authenticity_token = response.xpath("//input[@name='authenticity_token']/@value").extract_first()
        utf8 = response.xpath("//input[@name='utf8']/@value").extract_first()
        commit = response.xpath("//input[@name='commit']/@value").extract_first()
        post_data = dict(
            login=USERNAME,
            password=PASSWORD,
            authenticity_token=authenticity_token,
            utf8=utf8,
            commit=commit)
        yield scrapy.FormRequest("https://github.com/session",
                                 formdata=post_data,
                                 callback=self.after_login,
                                 errback=self.error_back)

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

