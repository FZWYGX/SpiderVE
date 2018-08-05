import requests
import re
from base64 import b64encode
from PIL import Image

from settings import USERNAME, PASSWORD, APPCODE


class QunarLogin(object):
    """
    登录去哪儿需要的cookie包括: QN, QN25, QN271, _i, _vi, fid
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
        # 登录页面
        self.login_url = 'https://user.qunar.com/passport/login.jsp'
        # 发起登录请求的url
        self.logined_url = 'https://user.qunar.com/passport/loginx.jsp'
        # 去哪儿网用户页面
        self.qunar_index = 'http://user.qunar.com/index/page'

    def start_get_session(self):
        sessionRe = requests.session()
        return sessionRe

    def get_base_cookies(self, sessionRe):
        """
        获取登录时需要的更多cookie
        """
        # 获得cookie参数QN1
        sessionRe.get(self.login_url, headers=self.headers)

        # 获得cookie参数QN25, 和新的QN1, 并下载图片
        response = sessionRe.get('https://user.qunar.com/captcha/api/image?k={en7mni(z&p=ucenter_login&c=ef7d278eca6d25aa6aec7272d57f0a9a')
        with open('captcha.png', 'wb') as f:
            f.write(response.content)

        # 获得cookie参数_i, _vi
        sessionRe.get('https://user.qunar.com/passport/addICK.jsp?ssl')

        # 获取seddionId, 经过查找发现seddionId在这个js文件中，所以先得到它
        response = sessionRe.get('https://rmcsdf.qunar.com/js/df.js?org_id=ucenter.login&js_type=0')

        # 查找seddionId, 通过正则得到sessionId
        seddionId = re.findall(r'&sessionId=(.*?)&', response.text)[0]

        # 获得cookie参数fid
        sessionRe.get('https://rmcsdf.qunar.com/api/device/challenge.json?callback=callback_1511693290383&sessionId={}&domain=qunar.com&orgId=ucenter.login'.format(seddionId))

        # 拿到QN271, 通过比对发现参数QN271和sessionId相同，所以直接加入cookies中
        sessionRe.cookies.update({'QN271': seddionId})
        return sessionRe

    def hand_captcha(self):
        """
        手动输入验证码
        """
        image = Image.open('captcha.png')
        image.show()
        code = input('请输入验证码:')
        return code

    def aliyun_captcha(self):
        """
        阿里云市场 - 图片验证码识别
        """
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

    def login(self, username, password):

        # 实例化一个session
        sessionRe = self.start_get_session()

        # 调用函数，在session中添加cookie
        sessionRe = self.get_base_cookies(sessionRe)

        # 试了很多次, 阿里云对于去哪儿网的验证码识别也不是很好
        # 获取验证码, (阿里云市场-图片验证码识别), 识别
        # code = self.aliyun_captcha()

        # 获取验证码, 手动输入
        code = self.hand_captcha()

        form_data = {
            'loginType': 0,
            'username': username,
            'password': password,
            'remember': 1,
            'vcode': code,
        }

        # 通过post请求方式，模拟登录
        resp = sessionRe.post(self.logined_url, form_data)
        # 不管是否登录成都, self.logined_url都会反馈信息
        print(resp.text)

        # 向去哪儿官网发起请求
        response = sessionRe.get(self.qunar_index)
        # 判断条件是您的用户名是否在网页中
        if response.status_code == 200:
            user_num = re.findall("个人信息", response.text)
            if len(user_num) > 0 and user_num[0] == "个人信息":
                print("这个网页有个人信息")
                print("登录成功")
            else:
                print("登录失败")
        else:
            print("response.status_code不是200")


if __name__ == '__main__':
    qunar = QunarLogin()
    qunar.login(username=USERNAME,
                password=PASSWORD)
