# -*- coding: utf-8 -*-
import scrapy
from huxiu.items import HuxiuItem
import re
global page
class TigerSpider(scrapy.Spider):
    name = 'tiger'
    allowed_domains = ['huxiu.com']
    start_urls = ['https://www.huxiu.com/index.php']

    def parse(self, response):
        global page
        num=len(response.xpath('//span[@class="author-name "]'))
        title_list=response.xpath('//a[@class="transition msubstr-row2"]/text()').extract()
        author_list=response.xpath('//span[@class="author-name "]/text()').extract()
        link_list=response.xpath('//a[@class="transition msubstr-row2"]/@href').extract()
        TIME_STAMP=response.xpath('//div[@class="get-mod-more js-get-mod-more-list transition"]/@data-last_dateline').extract()[0]
        print('*****************************************************************************************')
        print('GET TIMESTAMP:'+TIME_STAMP)
        form_data={'huxiu_hash_code': '7e60f03b00514b92a7ab248523bb7e75','page':'2','last_dateline':TIME_STAMP,}

        for i in range(num):
            item=HuxiuItem()
            item['title']=title_list[i]
            item['author']=author_list[i]
            item['link']='https://www.huxiu.com'+link_list[i]
            print (item['link'])
           # print('Author:'+item['author'])  the system will report ERROR message with code issue
            yield item
        page =2
        yield scrapy.FormRequest(url='https://www.huxiu.com/v2_action/article_list',formdata=form_data,callback=self.after_post)


    def after_post(self,response):
        global page
        patern_title='class="transition msubstr-row2" target="_blank">(.*)<'
        patern_author='<span class="author-name">(.*)<'
        patern_conent='<div class="mob-sub">(.*)<'
        patern_link='<a href="(.*)" class="transition msubstr-row2" target="_blank">'
        print('***************************Starting the AJAX Request !!!!!!!!!!!!!!!!!!!!!!*******************')
        print ("the server response code :" + str(response.status)) #NOTE: resonse.status is fucking useful to verify if the crawl has gotten the data
        # print (type(response.body))  NOTE: THE RESULT IS 'bytes'
        print('**********This is the crawl result of PAGE :'+ str(page) +'*************************************')
        data_trans=(response.body).decode('utf-8')  #NOTE: Transfer 'bytes' to 'str' Python 3 usful tool
        # print(type(data_trans))
        # print(data_trans)
        data_json=eval(data_trans)   # NOTE : TO Transfer the string to Dic type (amazing tools)
        # print('The type of data_json:')
        # print(type(data_json))  Note: it is Dict type
    #extract the data and found the dic
        DATA= data_json['data']
        TIME_STAMP=data_json['last_dateline']
        TOTAL_PAGE_NUMBER=int(data_json['total_page'])
        form_data = {'huxiu_hash_code': '7e60f03b00514b92a7ab248523bb7e75', 'page':str(page),'last_dateline':TIME_STAMP,}
        print("the new last_dateline:" + str(TIME_STAMP))
        title_list=re.compile(patern_title).findall(DATA)
        author_list=re.compile(patern_author).findall(DATA)
        link_list=re.compile(patern_link).findall(DATA)
        num_tilte= len(title_list)
        print("the number of Ariticle Titel:"+str(num_tilte))
        num_author = len(author_list)
        print("the number of Ariticle Author:" + str(num_author))
        print('*****************************************************************************************')
        for i in range(num_tilte):
             item = HuxiuItem()
             item['title'] = title_list[i][0:-5]
             item['author'] = author_list[i]
             link_trans=link_list[i][1:]
             link_final=link_trans[0:8]+link_trans[9:]
             item['link']='https://www.huxiu.com'+link_final
             #print(item['link'])
             yield item
        page=page+1
        if page>TOTAL_PAGE_NUMBER:
            print ("********************************The Data Scrawing Job completed succefully !!!************************************")
            return
        yield scrapy.FormRequest(url="https://www.huxiu.com/v2_action/article_list",formdata=form_data,callback= self.after_post)