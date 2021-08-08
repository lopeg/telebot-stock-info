"""
Uses news aggregation service https://stocknewsapi.com/
A paid subscruption is needed
"""
import requests


def get_news_by_symbol_ranked(symbol, token, number_of_items_to_show):
    """
    Get ranked list of news about specific company

    args: symbol - market ticker, i.e. MSFT
    args: token - authentication token for https://stocknewsapi.com/api
    args: number_of_items_to_show - how many news to show

    returns: json object with news url, title, source name and sentiment
    """

    url = "https://stocknewsapi.com/api/v1?tickers={}&sortby=rank&items={}&token={}".format(
        symbol, number_of_items_to_show, token
    )
    return requests.get(url=url).json()["data"]
