import yfinance as yf

from cachetools import cached
from finvizfinance.quote import finvizfinance

@cached(cache={})
def get_ticker_finvizfinance(symbol):
    """
    Get the whole symbol object from finvizfinance

    :param:  stock market ticker
    :return: object with all available data
    """
    return finvizfinance(symbol)

def get_target_price(symbol):
    """
    Get target stock price based on a Finviz Finance data

    :param:  stock market ticker
    :return: target price consensus
    """
    stock = get_ticker_finvizfinance(symbol)
    return stock.TickerFundament()['Target Price']

def get_chart(symbol, time_frame='weekly'):
    """
    Get chart url

    :param: stock market ticker
    :param: chart time frame. Allowed: daily, weekly (default), monthly.
    :return: url of tha saved chart. Chart is saved as {symbol}.jpg
    """
    stock = get_ticker_finvizfinance(symbol)
    return stock.TickerCharts(timeframe=time_frame, charttype='advanced', out_dir='.')


@cached(cache={})
def get_ticker(symbol):
    """
    Get the whole symbol object from yfinance

    :param:  stock market ticker
    :return: object with all available data
    """
    return yf.Ticker(symbol)


def get_current_price(symbol):
    """
    Retrieve a company stock price based on its ticker

    :param:  stock market ticker
    :return: rounded to 2 decimals price in USD, 0 - for not found
    :return: rounded to 2 decimals price change in %, 0 - for not found
    """
    ticker = get_ticker(symbol)

    todays_data = ticker.history(period="2d")

    if todays_data.empty:
        price, change = 0, 0
    else:
        price = todays_data["Close"][1]
        change = (todays_data["Close"][1] / todays_data["Close"][0] - 1) * 100

    return price, change


def get_financials(symbol):
    """
    Retrieve a company annual financials for last 4 years

    :param:  stock market ticker
    :return: dataFrame with annual financials for last 4 years in millions USD
    :return: dataFrame with quartely financials for last 4 quarters in millions USD
    """
    ticker = get_ticker(symbol)

    financials_annual = ticker.financials.dropna().astype(float) / 1000000
    financials_quarterly = ticker.quarterly_financials.dropna().astype(float) / 1000000

    return financials_annual, financials_quarterly


def get_financials_quarterly(symbol):
    """
    Retrieve a company annual financials for last 4 years

    :param: stock market ticker
    :return: dataFrame with financials for last 4 years in millions USD
    """
    ticker = get_ticker(symbol)
    return ticker.quarterly_financials.dropna().astype(float) / 1000000


def get_recommendations(symbol, rows=20):
    """
    Retrieve analysts recommendations about a stock

    :param: stock market ticker
    :param: number of the most recent recommendations to show
    :return: dataFrame with 20 recommendations to buy, hold or sell
    """
    ticker = get_ticker(symbol)
    return ticker.recommendations.tail(rows)


def get_holders(symbol):
    """
    Retrieve main holders of stocks

    :param: stock market ticker
    :return: major holders
    :return: 10 biggest institutional holders
    """
    ticker = get_ticker(symbol)
    return ticker.major_holders, ticker.institutional_holders
