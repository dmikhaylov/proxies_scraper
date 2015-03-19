import re
from io import BytesIO

from lxml import etree
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from proxies_scraper.items import ProxiesScraperItem


def unmask_ip(masking_styles, masked_ip_html):
    html = masked_ip_html
    for ms in masking_styles.strip().split('\n'):
        style_name, replace_style = ms.strip('.} ').split('{')
        html = html.replace(style_name, replace_style)
    html = re.sub(r"(?P<tag></.+?>)(?P<value>[\d\.]+)", r"\1<span>\2</span>", html)
    context = etree.iterparse(BytesIO(html.encode('utf-8')))
    for action, elem in context:
        if elem.tag == 'style':
            elem.clear()
            continue
        if 'style' in elem.attrib or 'class' in elem.attrib:
            attr = elem.attrib.get('style') or elem.attrib.get('class')
            if 'none' in attr and action == 'end':
                elem.clear()

    html = etree.tostring(context.root, method="html")
    html =  re.sub(r'<[^>]*?>', '', html)
    html = re.sub(r'\s+', '' , html)
    return html


class HidemyassSpider(CrawlSpider):
    name = 'hidemyass'
    allowed_domains = ['hidemyass.com']
    start_urls = ['http://proxylist.hidemyass.com/']

    rules = (
        Rule(SgmlLinkExtractor(allow=r'/\d+'), callback='parse_items', follow=True),
    )

    def parse_items(self, response):
        hxs = HtmlXPathSelector(response)
        rows = hxs.select('//td[@class="leftborder timestamp"]/parent::tr')
        for row in rows:
            i = ProxiesScraperItem()
            i['last_update'] = int(row.select('td[@class="leftborder timestamp"]/@rel').extract()[0])
            masking_styles = row.select('td[2]/span/style/text()').extract()[0]
            masked_ip_html = row.select('td[2]').extract()[0]
            i['ip_address'] = unmask_ip(masking_styles, masked_ip_html)
            i['port'] = int(row.select('td[3]/text()').extract()[0])
            i['country'] = row.select('td[4]/span//text()').extract()[1].strip()
            i['speed'] = int(row.select('td[5]/div/@rel').extract()[0])
            i['connection_time'] = int(row.select('td[6]/div/@rel').extract()[0])
            i['type'] = row.select('td[7]/text()').extract()[0].strip()
            i['anonymity'] = row.select('td[8]/text()').extract()[0].strip()

            yield i
