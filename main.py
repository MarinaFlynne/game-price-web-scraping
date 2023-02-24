"""
Price scraping tool
"""
import requests
from bs4 import BeautifulSoup
import yaml

# import pandas as pd

URL_FILE = 'games.yaml'


def main():
    # get the urls
    file = open(URL_FILE)
    data = yaml.safe_load(file)
    file.close()

    games: dict = {}
    for game in data:
        request = requests.get(game['url'])

        soup = BeautifulSoup(request.content, 'html.parser')

        # get the game details
        title = soup.select_one('.prodTitle')
        title = title.select_one('span').text.strip()
        print(title)
        try:
            new_price = soup.select_one('.pricetext').text.strip().replace('$', '')
            print(f'price: {new_price}')
        except AttributeError:
            pass
        try:
            used_price = soup.select_one('.pricetext1').text.strip().replace('$', '')
            print(f'used price: {used_price}')
        except AttributeError:
            pass
        print()


if __name__ == '__main__':
    main()
