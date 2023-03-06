"""
Price scraping tool
"""
import sqlite3

import requests
from bs4 import BeautifulSoup
import re
import time

import pandas as pd

GAMES_FILE = 'Games.csv'
DATABASE_FILENAME = 'games.db'


def main():
    # create dataframe from games CSV file
    games_df: pd.DataFrame = pd.read_csv(GAMES_FILE)
    print(games_df)

    scrape_websites(games_df)


def scrape_websites(games_df):
    for index, game in games_df['Game'].items():
        if index < 200:
            print(f'{index}: {game}')
            link = get_link(game)
            game_data: dict = scrape_gamestop(link)
            if game_data['title'] != 'NULL':
                # change title
                game_data['title'] = game.replace("'", "")
                game_data['link'] = game_data['link'].replace("'", "")
                add_game_to_db(game_data)
            print()
            time.sleep(3)


def does_game_exist(title: str):
    """
    Checks if the given game exists in the database already
    :param title:
    :return:
    """
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM games WHERE title = '{title}'")
    row = cursor.fetchone()

    connection.close()
    # return result
    if row is not None:
        return True
    else:
        return False


def add_game_to_db(game_details: dict):
    if does_game_exist(game_details['title']):
        print("game already in db")
        return

    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()

    for key in game_details.keys():
        if game_details[key] != 'NULL':
            game_details[key] = f"\'{game_details[key]}\'"
    print(game_details)
    print(
        f"Adding title: {game_details['title']}, link: {game_details['link']}, price: {game_details['price']}, used_price: {game_details['used_price']}")
    cursor.execute(
        f"INSERT INTO games (title, link, price, used_price) VALUES ({game_details['title']}, {game_details['link']}, {game_details['price']}, {game_details['used_price']})")
    connection.commit()
    connection.close()
    # print(f"Added title: {game_details['title']}, link: {game_details['link']}, price: {game_details['price']}, used_price{game_details['used_price']}")


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

    game_details: dict = {'title': 'NULL',
                          'link': game_url,
                          'price': 'NULL',
                          'used_price': 'NULL'}
    # get the game details
    title_element = soup.select_one('.prodTitle')
    try:
        game_details['title'] = title_element.select_one('span').text.strip()
        # print(f"game title: {game_details['title']}")
    except AttributeError:
        print("unable to find")
        return game_details
    try:
        game_details['price'] = soup.select_one('.pricetext').text.strip().replace('$', '')
        # print(f"price: {game_details['price']}")
    except AttributeError:
        pass
    try:
        game_details['used_price'] = soup.select_one('.pricetext1').text.strip().replace('$', '')
        # print(f"used price: {game_details['used_price']}")
    except AttributeError:
        pass
    return game_details


if __name__ == '__main__':
    main()
