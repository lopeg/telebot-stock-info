import os

import telebot
import random
import stock_api as sa
import news_api as na

import dataframe_image as dfi

# token is generated during the activation by https://telegram.me/BotFather
# format "77777777777:FMSMBDSHGDJDSBHMSBSHDGHSGDJHGFJHF"
bot = telebot.TeleBot(os.environ.get("TELEBOT_TOKEN"))


@bot.message_handler(commands=["start", "help"])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "Greetings! I can show you basic financial info based on a ticker.\n"
        + "Data comes from free yfinance API and limited by 5 requests per second.\n"
        + "/p <ticker> : price\n"
        + "/r <ticker> : analysts' recommendations\n"
        + "/n <ticker> \{number_of_news\}: financial ranked (10 by default) news\n"
        + "/f <ticker> : financials stats\n"
        + "/c <ticker> : chart\n"
        + "/h <ticker> : holders",
    )


def extract_arg(arg):
    return arg.split()[1:]


@bot.message_handler(commands=["p"])
def price(message):
    ticker = extract_arg(message.text)[0].upper()
    price_current, change = sa.get_current_price(ticker)
    price_target = sa.get_target_price(ticker)
    if price == 0:
        text = "No data found, {} may be delisted".format(ticker)
    else:
        text = "{}\nCurrent price: {:0.2f} USD.\nToday's move: {:+0.2f}%.\nTarget price: {} USD".format(
            ticker, price_current, change, price_target
        )

    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["f"])
def financials(message):
    ticker = extract_arg(message.text)[0].upper()
    financials_y, financials_q = sa.get_financials(ticker)

    if financials_y.empty or financials_q.empty:
        bot.send_message(
            message.chat.id, "No data found, {} may be delisted".format(ticker)
        )
    else:
        dfi.export(financials_y, "financials_y.png", table_conversion="matplotlib")
        bot.send_photo(
            message.chat.id,
            photo=open("financials_y.png", "rb"),
            caption="Annual, MM USD",
        )

        dfi.export(financials_q, "financials_q.png", table_conversion="matplotlib")
        bot.send_photo(
            message.chat.id,
            photo=open("financials_q.png", "rb"),
            caption="Quarterly, MM USD",
        )


@bot.message_handler(commands=["c"])
def chart(message):
    ticker = extract_arg(message.text)[0].upper()
    price_target = sa.get_target_price(ticker)
    if price == 0:
        text = "No data found, {} may be delisted".format(ticker)
    else:
        sa.get_chart(ticker)
        bot.send_photo(
            message.chat.id,
            photo=open("{}.jpg".format(ticker), "rb")
        )
        os.remove("{}.jpg".format(ticker))

@bot.message_handler(commands=["h"])
def holders(message):
    ticker = extract_arg(message.text)[0].upper()
    holders_main, holders_inst = sa.get_holders(ticker)

    if holders_main.empty or holders_inst.empty:
        bot.send_message(
            message.chat.id, "No data found, {} may be delisted".format(ticker)
        )
    else:
        dfi.export(holders_main, "holders_main.png", table_conversion="matplotlib")
        bot.send_photo(
            message.chat.id,
            photo=open("holders_main.png", "rb"),
            caption="Main holders",
        )

        dfi.export(holders_inst, "holders_inst.png", table_conversion="matplotlib")
        bot.send_photo(
            message.chat.id,
            photo=open("holders_inst.png", "rb"),
            caption="Institutional holders",
        )


@bot.message_handler(commands=["r"])
def recommendations(message):
    ticker = extract_arg(message.text)[0].upper()
    recommendations = sa.get_recommendations(ticker)

    if recommendations.empty:
        bot.send_message(
            message.chat.id, "No data found, {} may be delisted".format(ticker)
        )
    else:
        dfi.export(
            recommendations, "recommendations.png", table_conversion="matplotlib"
        )
        bot.send_photo(message.chat.id, photo=open("recommendations.png", "rb"))


@bot.message_handler(commands=["n"])
def recommendations(message):
    news_args = extract_arg(message.text)
    ticker = news_args[0].upper()
    number_of_items_to_show = news_args[1] if len(news_args) == 2 else 10

    # token is generated during the activation by https://stocknewsapi.com/
    token = os.environ.get("STOCKNEWSAPI_TOKEN")

    all_news = na.get_news_by_symbol_ranked(ticker, token, number_of_items_to_show)

    if not all_news:
        text = "No data found, {} may be delisted".format(ticker)
    else:
        text = "Top {} news for {}:\n".format(number_of_items_to_show, ticker)
        for news in all_news:
            if news["sentiment"] == "Positive":
                sentiment = "&#x1F446"
            elif news["sentiment"] == "Negative":
                sentiment = "&#x1F447"
            else:
                sentiment = "&#x1F449"
            text += "{} <a href='{}'>{}</a>\n".format(
                sentiment, news["news_url"], news["title"]
            )

    bot.send_message(
        message.chat.id, text, parse_mode="HTML", disable_web_page_preview=True
    )


@bot.message_handler(commands=["o"])
def easter_egg(message):
    answers = [
        "у безоса спроси",
        "а-м-а-з-о-о-о-о-н!!",
        "та уже все в чате знают",
        "на а начинается на зон заканчивается",
    ]
    bot.send_message(message.chat.id, random.choice(answers))


bot.polling()
