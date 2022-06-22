import requests
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_Endpoint = "https://www.alphavantage.co/query"
STOCK_API_KEY = "YOUR STOCK API KEY"
NEWS_Endpoint = "https://newsapi.org/v2/everything"
NEWS_API_KEY = "YOUR NEWS API KEY"
TWILIO_SID = "YOUR TWILIO SID"
TWILIO_TOKEN = "YOUR TWILIO TOKEN"
FROM_CELLPHONE_NUMBER = "FROM CELLPHONE NUMBER"
TO_CELLPHONE_NUMBER = "TO CELLPHONE NUMBER"


def get_stock_value_time_series():
    stock_parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey": STOCK_API_KEY,
    }

    response = requests.get(url=STOCK_Endpoint, params=stock_parameters)
    response.raise_for_status()
    alpha_data = response.json()["Time Series (Daily)"]
    return alpha_data


def get_value_difference_percent(stock_data):
    stock_data_list = [value for (key, value) in stock_data.items()]
    yesterday_closing_price = stock_data_list[0]["4. close"]
    before_yesterday_closing_price = stock_data_list[1]["4. close"]

    difference = (float(yesterday_closing_price) - float(before_yesterday_closing_price))

    diff_percent = round(difference / float(yesterday_closing_price) * 100)
    return diff_percent


def get_company_news():
    news_parameters = {
        "qInTitle": COMPANY_NAME,
        "apiKey": NEWS_API_KEY,
    }

    news_response = requests.get(url=NEWS_Endpoint, params=news_parameters)
    news_response.raise_for_status()

    articles = news_response.json()["articles"]
    three_articles = articles[:3]
    return three_articles


def send_sms(up_or_down, difference_percent, articles):

    messages_list = [f"\nHeadline: {article['title']}. \nBrief: {article['description']}" for article in articles]
    formatted_messages_list = "\n".join(messages_list)
    message_body = f"{STOCK}: {up_or_down}{difference_percent}% \n {formatted_messages_list}"

    client = Client(TWILIO_SID, TWILIO_TOKEN)
    message = client.messages.create(
        body=message_body,
        from_=FROM_CELLPHONE_NUMBER,
        to=TO_CELLPHONE_NUMBER,
    )
    print(message.status)


def main():
    stock_data = get_stock_value_time_series()
    difference_percent = get_value_difference_percent(stock_data)

    if difference_percent > 0:
        up_or_down = "🔺"
    else:
        up_or_down = "🔻"

    if abs(difference_percent) >= 5:
        articles = get_company_news()
        send_sms(up_or_down, difference_percent, articles)


main()
