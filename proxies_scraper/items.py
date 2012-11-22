# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ProxiesScraperItem(Item):
    # define the fields for your item here like:
    # name = Field()

    last_update = Field()
    ip_address = Field()
    port = Field()
    country = Field()
    speed = Field()
    connection_time = Field()
    type = Field()
    anonymity = Field()

#    Last update	IP address	Port	Country	Speed	Connection time	Type	Anonymity
