"""
Price scraping tool
"""
import requests
from bs4 import BeautifulSoup
import re
import time

import pandas as pd

GAMES_FILE = 'Games.csv'


def main():
    # create dataframe from games CSV file
    games_df: pd.DataFrame = pd.read_csv(GAMES_FILE)
    print(games_df)

    for index, game in games_df['Game'].items():
        if index < 60:
            print(f'{index}: {game}')
            link = get_link(game)
            print(link)
            scrape_gamestop(link)
            print()
            time.sleep(3)


def get_link(game_title: str) -> str:
    """Gets links to gamestop page for given game title
        Parameters
        ----------
            game_title:
                the game title to search for
        Returns
        -------
        str
            the link to the games page
    """
    # replace all non-alphanumeric characters with '-'
    # formatted_game_title = re.sub('[^0-9a-zA-Z]+', '+', game_title).lower()
    formatted_game_title = re.sub(r"[ :]+", "-", game_title)
    # get search results page for our game
    url = f'https://www.gamestop.ca/SearchResult/QuickSearch?q={formatted_game_title}&productType=2'
    print(f'formatted Title: {formatted_game_title}')
    print(f'search url: {url}')
    request = requests.get(url)
    soup = BeautifulSoup(request.content, 'html.parser')

    # select all the game links
    links = soup.find_all(class_='desktopSearchProductTitle')

    # check if we are on search results page or games page
    if not links:
        return url

    game_link = 'https://www.gamestop.ca'
    for link in links:
        if str(link.text.strip()) == game_title:
            game_link += link.select_one('a')['href']
            break

    return game_link


def scrape_gamestop(game_url: str) -> dict:
    request = requests.get(game_url)

    soup = BeautifulSoup(request.content, 'html.parser')
    
    game_details: dict = {'title': 'No title found', 'price': 'No price found', 'used price': 'No used price found'}
    # get the game details
    title_element = soup.select_one('.prodTitle')
    try:
        game_details['title'] = title_element.select_one('span').text.strip()
        print(f"game title: {game_details['title']}")
    except AttributeError:
        print("unable to find")
        return game_details
    try:
        game_details['price'] = soup.select_one('.pricetext').text.strip().replace('$', '')
        print(f"price: {game_details['price']}")
    except AttributeError:
        pass
    try:
        game_details['used price'] = soup.select_one('.pricetext1').text.strip().replace('$', '')
        print(f"used price: {game_details['used price']}")
    except AttributeError:
        pass


if __name__ == '__main__':
    main()
