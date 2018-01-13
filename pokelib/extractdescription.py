from lxml import html
import requests
from pprint import pprint

page = requests.get("https://www.pokemon.com/us/pokedex/bulbasaur")

content = page.text.replace('\n', '').replace('\r', '')

tree = html.fromstring(content)

description = tree.xpath('//p[@class="version-y                                  active"]/text()')

pprint(description[0].strip())


type = tree.xpath('//div[@class="column-7 push-7"]/ul/li/span[@class="attribute-value"]/text()')

pprint(type[0].strip())
