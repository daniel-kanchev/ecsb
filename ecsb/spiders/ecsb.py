import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from ecsb.items import Article


class ecsbSpider(scrapy.Spider):
    name = 'ecsb'
    start_urls = ['https://www.ecsb.com/community/in-our-community/news-events']

    def parse(self, response):
        links = response.xpath('//article/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('(//li[@class="page-item"])[last()]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//section[@class="breadcrumbs"]//ul/li[last()]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//h4/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//section[@aria-label="News & Events Article"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
