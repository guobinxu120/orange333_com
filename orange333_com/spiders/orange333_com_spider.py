# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy import Request, FormRequest
from urlparse import urlparse
from json import loads
from datetime import date
import re,json

class orange333_comSpider(scrapy.Spider):

    name = "orange333_com_spider"

    use_selenium = True
###########################################################

    def __init__(self, *args, **kwargs):
        super(orange333_comSpider, self).__init__(*args, **kwargs)

###########################################################

    def start_requests(self):
        form_header = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ko;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            # 'Content-Length': '401',
            'Content-Type': 'application/json;charset=UTF-8',
            'Cookie': '_ga=GA1.2.1988657352.1554121568; _gid=GA1.2.1896111374.1554121568',
            # 'Host': 'www.orange333.com',
            # 'Origin': 'https://www.orange333.com',
            # 'Pragma': 'no-cache',
            # 'Referer': 'https://www.orange333.com/d/index.html',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
            # 'X-App-Version': '3.6.4.9',
            # 'X-Client': 'desktop',
            'X-Client-Id': '1988657352.1554121568',
            'X-Client-Info': 'b48623e759c240560514ba3e10f353fa',
            'X-User-Id': '',
            # 'X-xid': '19e1cd89-02e8-4c63-9ffb-8b05622e060w'
        }

        form_data = {
            'password': "virat123",
            'recaptchaResponse': "03AOLTBLSnIBwyQj86apdSBnr55PL7ChSu9994CPDc03054FrD3CoyG7iMkmCNOwgR53Oj7WWvj6ynrLIEXYvAsN8_yFjMB6bsg31gO6tvABu0loyZ1zm8lzKJVN8KqYDZIeIuJR_i9rPOaZn_FtQAYs0P20jmmQXRc6TEhK4su2kMa-U2yKvwJKsCGuoObTCHygSdjIcXSwWuKBpCqM6yv3Jy2FTP8TPaB7vHbT435Pj9joeuCSIP0S40BpqMhY_SDNMYrMaIyKJ2v_WmmKZZl_BWJOJ7w4TMxiHe4tCrVzx0J24QHW8edxlJAEZmbDsQwc82Hjj9HVl-",
            'username': "d101010"
        }
        yield Request('https://www.orange333.com/api/auth/login', method='POST', headers=form_header, callback=self.parse, body=json.dumps(form_data), dont_filter=True)

###########################################################

    def parse(self, response):
        load_url = ''
        if response.meta['page_count'] == 1:
            load_url = response.body.split('load(\'/buscapagina?')[-1].split('\' + pageclickednumber')[0]
            response.meta['load_url'] = load_url
        else:
            load_url = response.meta['load_url']

        
        products = response.xpath('//*[contains(@class, "prod prod-")]')

        print len(products)
        print "###########"
        print response.url

        if not products: return
        
        for i in products:
            item = {}

            item['Vendedor'] = 448
            item['ID'] = i.xpath('./@data-id').extract_first()
            item['Title'] = i.xpath('.//*[@class="title ellipsis"]/text()').extract_first()
            #item['Description'] = ''

            price = i.xpath('.//*[@class="price priceFixed"]//text()').re(r'[\d.,]+')

            if not price:
                price = i.xpath('.//*[@class="price big priceFixed"]//text()').re(r'[\d.,]+')

            if not price:
                price = i.xpath('.//*[@class="price fixPrice"]//text()').re(r'[\d.,]+')

            if not price:
                price = i.xpath('.//*[@class="list-price fixPrice"]//text()').re(r'[\d.,]+')

            item['Price'] = ''
            
            if price:
                price[0] = price[0].replace('.', '').replace(',', '.')
                # price[0] = price[0].replace(',', '.')
                # if price[0].count('.') == 2:
                #     price[0] = price[0].replace('.', '', 1)
                item['Price'] = price[0]
                item['Currency'] = 'CLP'
            else:
                continue

            item['Category URL'] = response.meta['CatURL']
            item['Details URL'] = response.urljoin(i.xpath('.//*[@class="title ellipsis"]/@href').extract_first())
            item['Date'] = date.today()

            if price:
                yield item


        # count = len(response.xpath('//ul[@class="pagination"]/li'))
        # next = response.xpath('//*[@class="next_page"]/@href').extract_first()
        # if next:
        response.meta['page_count'] += 1
        yield Request('https://store.sony.cl/buscapagina?{}{}'.format(load_url, response.meta['page_count']), callback=self.parse, meta=response.meta)
        