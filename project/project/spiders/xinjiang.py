import scrapy
from project.items import ProjectItem
from lxml import etree
from PIL import Image
import requests
import pytesseract
import re

class XinjiangSpider(scrapy.Spider):
    name = 'xinjiang'
    allowed_domains = ['gov.cn']
    start_urls = ['http://swt.xinjiang.gov.cn/swt/zcfg/list.shtml'] 
   
    #start_urls = ['https://www.klmy.gov.cn/010/010005/secondpage.html'] 

    def parse(self, response):
        #列表标题和内容页url
        start='<!--列表 开始-->'
        end='<!--列表 结束-->'

        match=re.search(start+'.*?'+end,response.text,re.S)
        html=etree.HTML(match.group())
        titleList=html.xpath('//a/@title')
        urlList=html.xpath('//a/@href')
        #urlList=[x for x in urlList if 'javascript' not in x]
        self.file=open("xinjiang.txt","w",encoding='utf-8')
        for i in range(len(urlList)):
            self.file.write(titleList[i]+"\n")
            self.file.write(urlList[i]+"\n")
            url=response.urljoin(urlList[i])
            yield scrapy.Request(url=url,callback=self.crawlText)

    #获取分页中的文字,包括图片中的文字
    def crawlText(self,response):
        #print(response.text)
        #文字
        html=etree.HTML(response.text)
        #text=response.css('div,p,span::text').extract()
        #chinese=re.findall('[\u4e00-\u9fa5]',response.text,re.S)
        text=self.filter_tags(response.text)
        
        file=open("xinjiang.txt","a",encoding='utf-8')
        file.write(''.join(text))

        #图片
        imgList=html.xpath('//img/@src')
        for img in imgList:
            url=response.urljoin(img)
            print(url)
            image=Image.open(url)
            #result=pytesseract.image_to_string(image,lang="chi_sim")

        

      



 
    def filter_tags(self,htmlstr):
        #先过滤CDATA
        re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
        re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
        re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
        re_br=re.compile('<br\s*?/?>')#处理换行
        re_h=re.compile('</?\w+[^>]*>')#HTML标签
        re_comment=re.compile('<!--[^>]*-->')#HTML注释
        s=re_cdata.sub('',htmlstr)#去掉CDATA
        s=re_script.sub('',s) #去掉SCRIPT
        s=re_style.sub('',s)#去掉style
        s=re_br.sub('\n',s)#将br转换为换行
        s=re_h.sub('',s) #去掉HTML 标签
        s=re_comment.sub('',s)#去掉HTML注释
        #去掉多余的空行
        blank_line=re.compile('\n+')
        s=blank_line.sub('\n',s)
        s=self.replaceCharEntity(s)#替换实体
        return s

    def replaceCharEntity(self,htmlstr):
        CHAR_ENTITIES={'nbsp':' ','160':' ',
            'lt':'<','60':'<',
            'gt':'>','62':'>',
            'amp':'&','38':'&',
            'quot':'"','34':'"',}
    
        re_charEntity=re.compile(r'&#?(?P<name>\w+);')
        sz=re_charEntity.search(htmlstr)
        while sz:
            entity=sz.group()#entity全称，如>
            key=sz.group('name')#去除&;后entity,如>为gt
            try:
                htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
                sz=re_charEntity.search(htmlstr)
            except KeyError:
                #以空串代替
                htmlstr=re_charEntity.sub('',htmlstr,1)
                sz=re_charEntity.search(htmlstr)
        return htmlstr
  
            
            
            


        

