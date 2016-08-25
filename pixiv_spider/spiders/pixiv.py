# -*- coding: utf-8 -*-
import scrapy
import urllib
import os
import requests


class PixivSpider(scrapy.Spider):
    name = "pixiv"
    allowed_domains = ["pixiv.net"]

    def __init__(self, category, score):
        scrapy.Spider.__init__(self)
        self.keyword = category
        self.score = int(score)
        self.start_urls = (
            'http://www.pixiv.net/search.php?word=' +
            urllib.quote(self.keyword.encode('utf-8', 'replace')),
        )
        self.file = open('src.txt', 'w')
        if not os.path.isdir(self.keyword):
            os.makedirs(self.keyword)

    def parse(self, response):
        base_url = 'http://www.pixiv.net/search.php'
        sel = scrapy.Selector(response)
        total = int(
            sel.xpath('//span[@class="count-badge"]/text()').extract()[0][:-7])
        page_num = total / 20 + 1
        for i in range(page_num):
            url = base_url + '?word=' + \
                urllib.quote(self.keyword.encode(
                    'utf-8', 'replace')) + '&p=' + urllib.quote(str(i + 1).encode('utf-8'))
            yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        base_url = 'http://www.pixiv.net'
        sel = scrapy.Selector(response)
        links = sel.xpath('//a[@class="work  _work "]/@href').extract()
        for link in links:
            yield scrapy.Request(base_url + link, callback=self.parse_img)

    def parse_img(self, response):
        sel = scrapy.Selector(response)
        src = sel.xpath(
            '//img/@src').extract()[3]
        score = int(
            sel.xpath('//section[@class="score"]//span[@class="views"]/text()').extract()[1])
        if score >= self.score:
            self.download_image_file(src, response.url)

    def download_image_file(self, img_url, referer):
        url = img_url.split('.net')[0] + '.net' \
            '/img-original/img' + \
            '_'.join(img_url.split('img')[-1].split('_')[:-1]) + '.jpg'
        local_filename = referer.split('=')[-1]
        # here we need to set stream = True parameter
        img = requests.get(url, headers={
                           'Referer': referer, 'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/" +
                           "537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36"}, stream=True)
        if len(img.content) > 60:
            print "---------Downloading Image File:", local_filename, '.jpg-------------\n'
            with open(self.keyword + '/' + local_filename + ".jpg", 'wb') as f:
                for chunk in img.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                f.flush()
        return local_filename
