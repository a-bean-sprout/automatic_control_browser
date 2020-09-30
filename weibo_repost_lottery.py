# -*- coding: utf-8 -*-
import time
import json
from selenium import webdriver
from loguru import logger
import random

chrome_driver = r"./chromedriver"


class WB:
    def __init__(self):

        # 读参数信息
        with open('data.json', 'r') as file:
            data = json.load(file)
            self.username = data['username']
            self.password = data['password']
            self.refreshTime = data['refreshTime']
            self.isShow = data['isShow']
            self.isRepeatForward = data['isRepeatForward']
            logger.info(data)

        # 浏览器参数设置
        option = webdriver.ChromeOptions()
        if self.isShow == 'False':
            option.add_argument('--headless')
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-dev-shm-usage')
        option.add_argument('--disable-gpu')
        option.add_experimental_option('mobileEmulation', {'deviceName': 'iPhone X'})
        option.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        self.driver = webdriver.Chrome(chrome_options=option, executable_path=chrome_driver)  # 选择Chrome浏览器
        self.driver.implicitly_wait(30)  # 隐性等待

    def login(self):

        time.sleep(2)
        self.driver.find_element_by_class_name("b-left").click()

        # 登陆
        time.sleep(3)
        self.driver.find_element_by_id("loginName").send_keys(self.username)
        self.driver.find_element_by_id("loginPassword").send_keys(self.password)
        self.driver.find_element_by_id("loginAction").click()

        # sleep给浏览器留出反应时间
        time.sleep(5)

    def thisClick(self, element):
        try:
            self.driver.execute_script("arguments[0].click();", element)
            time.sleep(2)
        except Exception as e:
            logger.error(e)

    def start(self):

        # 登陆微博
        self.driver.get("https://m.weibo.cn/login?backURL=https%3A%2F%2Fm.weibo.cn%2F")
        self.login()
        time.sleep(3)

        while True:
            try:
                # 开始转发抽奖信息
                self.forward()
                time.sleep(int(self.refreshTime))

            except Exception as e:
                logger.error(e)


    def scroll(self):
        """该函数用户下滑页面"""

        num = random.randint(2, 10)
        logger.info("下滑次数为:" + str(num))

        for i in range(num):
            self.driver.execute_script("var q=document.documentElement.scrollTop=300000")
            time.sleep(3)

    def forward(self):

        # 搜索抽奖信息
        self.driver.get('https://m.weibo.cn/search?containerid=100103type%3D1%26q%3D%E6%8A%BD%E5%A5%96')
        time.sleep(3)

        # 下滑页面以获取更多的抽奖信息
        self.scroll()

        # 获取抽奖微博
        elements = self.driver.find_elements_by_css_selector(".weibo-member .card-wrap")
        element = random.choice(elements)
        text = element.find_element_by_class_name("weibo-og").text

        logger.info("该页面微博数量为:" + str(len(elements)))
        logger.info("待转发微博为:" + text)

        with open('./record.txt', "r") as f:
            previous = f.read()

        # 判断是否曾转发
        if not previous.count(text):

            # 进入详情页
            self.thisClick(element.find_element_by_css_selector(".weibo-og .weibo-text"))

            # 执行微博点赞操作
            self.thisClick(self.driver.find_element_by_css_selector(".lite-page-editor .lite-iconf-like"))

            '''
            # 执行微博评论的点赞操作
            like=self.driver.find_elements_by_class_name('lite-iconf-like');
            for i in like:
                self.thisClick(i)  # 点赞
            '''

            # 转发+评论
            values = ['中奖选我选我选我', '你这条转发评论是最近的巅峰',
                      '好运锦鲤 捞我吧', '祝我好运',
                      '所有好运非你莫鼠', '人生不长唯有暴富',
                      '何以解忧，唯有暴富', '何以解忧，唯有中奖', ]
            value = random.choice(values)
            self.thisClick(self.driver.find_element_by_class_name("lite-iconf-report"))  # 转发
            self.driver.find_element_by_css_selector(".m-pos-r textarea").send_keys(value)
            self.thisClick(self.driver.find_element_by_class_name("m-checkbox"))  # 同时评论
            self.thisClick(self.driver.find_element_by_class_name("m-send-btn"))  # 发送

            # 关注
            self.thisClick(self.driver.find_element_by_css_selector(".weibo-top .m-avatar-box a"))
            followBtns = self.driver.find_elements_by_class_name("m-followBtn")
            for i in followBtns:
                self.thisClick(i)  # 关注

            logger.info(text + "    评论内容：" + value)

            # 记入文件
            f = open('转发点赞记录.txt', "a+")
            f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "，" + text + "    评论内容：" + value + '\r')
            f.close()

        else:

            if previous.count(text):
                logger.info("已转发")
            if len(element.find_elements_by_css_selector(".weibo-og")) <= 0:
                logger.info("无法进入详情页")

        logger.info("************************")


if __name__ == '__main__':
    wb = WB()
    wb.start()
