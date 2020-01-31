import requests
import redis
import random
import re
import time
from lxml import etree
from fake_useragent import UserAgent


REDIS_HOST = '192.168.1.247'
REDIS_PORT = 6379
REDIS_PASSWORD = '19940327'
REDIS_LIST_NAME = "proxies"
REDIS_SORTED_SET_NAME = "proxies_sorted_set"
# HEADER = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0', 'Connection':'keep-alive'}
url_init = 'https://www.zymblog.top'
next_page_prefix = 'https://www.zymblog.top/blog/'


class mysite_spider(object):

    def __init__(self, host=REDIS_HOST, port=REDIS_PORT):
        # if REDIS_PASSWORD:
        #     self.reids_db = redis.Redis(host=host, port=port, password=REDIS_PASSWORD)
        # else:
        #     self.reids_db = redis.Redis(host=host, port=port)
        # 实例化UserAgent()
        self.useragent = UserAgent()

    # 返回随机头部
    def get_random_user_agent(self):
        header = {}
        header['User-Agent'] = self.useragent.random
        return header

    # def get_proxy_from_redis(self):
    #     # 从redis队列右边也就是最新取出一个代理并返回
    #     try:
    #         proxy_rank = random.choice(range(self.reids_db.zcard(REDIS_SORTED_SET_NAME)))
    #         for i in self.reids_db.zrange(REDIS_SORTED_SET_NAME, proxy_rank, proxy_rank):
    #             proxy = i
    #         return proxy
    #     except:
    #         print('存储代理的redis数据库为空！')

    def proxy_list_to_dict(self, proxy_list):
        try:
            proxy = re.split(r':', proxy_list)
            ip = re.split(r'/', proxy[1])[-1]
            protocol = proxy[0]
            port = proxy[2]
            proxy_dict = {}
            proxy_dict[protocol] = '{0}:{1}'.format(ip, port)
            return proxy_dict
        except Exception as e:
            print('proxy_list_to_dict错误：', e)

    # def delete_proxy(self, proxy):
    #     if self.reids_db.zrem(REDIS_SORTED_SET_NAME, proxy):
    #         print('%s 代理删除成功！' % proxy)

    def start_crawl_mysite(self):
        next_url = 'https://www.zymblog.top/blog/?page=1'
        while True:
            # proxy_str = str(self.get_proxy_from_redis(), encoding='utf8')
            # proxy_dict = self.proxy_list_to_dict(proxy_str)
            header_page = self.get_random_user_agent()
            response = requests.get(next_url, headers=header_page, timeout=4)
            response_text = response.text
            selector = etree.HTML(response_text)
            if response.status_code == 200:

                tiezis = selector.xpath("//div[@class='panel-body']/ul/div[@class='blog']")
                for each in tiezis:
                    tiezi_link = ''.join(each.xpath("./h3/a/@href"))
                    full_tiezi_link = url_init + str(tiezi_link)
                    tiezi_name = ''.join(each.xpath("./h3/a/text()"))

                    while True:
                        if random.choice([1, 2]) == 1:
                            tiezi_header = self.get_random_user_agent()
                            print('正在访问帖子 %s' % tiezi_name)
                            time.sleep(random.randint(1, 3) + random.randint(1, 5) / 10)
                            tiezi_data = requests.get(full_tiezi_link, headers=tiezi_header, timeout=4)
                        else:
                            break
                pagination = selector.xpath("//div[@class='paginator']/ul[@class='pagination']/li")
                try:
                    next_url_suffix = ''.join((pagination[-1].xpath("./a/@href")))
                    if next_url_suffix:
                        next_url = next_page_prefix + next_url_suffix
                    else:
                        print('爬取结束！')
                        break
                except Exception as e:
                    print('start_crawl_mysite：出错！因为%s' %e)
            else:
                pass
                # print('代理%s不可用，从redis中删除' % proxy_str)
                # self.delete_proxy(proxy_str)

            # 模拟随机停止爬取
            if random.choice(range(10)) == 1:
                break


if __name__ == '__main__':
    mysite_spider = mysite_spider()
    for i in range(6):
        print('进行第%s次爬取！' % str(i + 1))
        mysite_spider.start_crawl_mysite()
