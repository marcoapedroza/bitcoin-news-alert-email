import requests
import pandas as pd
from datetime import date, timedelta
import smtplib

# CONSTANTS
ALPHA_VANTAGE_API = "https://www.alphavantage.co/query"
NEWS_API = "http://newsapi.org/v2/everything"

API_KEY_ALPHA = ""
API_KEY_NEWS = ""
FROM_EMAIL = ""
TO_EMAIL = ""
EMAIL_PASSWORD = ""

ASSET_NAME = "BTC"
ASSET_NEWS = "bitcoin"
CURRENCY_MARKET = "BRL"

# Parameters - price - request
asset_params = {
    "function": "DIGITAL_CURRENCY_DAILY",
    "symbol": ASSET_NAME,
    "market": CURRENCY_MARKET,
    "apikey": API_KEY_ALPHA
}

response = requests.get(ALPHA_VANTAGE_API, params=asset_params)
data = response.json()['Time Series (Digital Currency Daily)']

btc_list = [price for (day, price) in data.items()]
date_list = [day for (day, price) in data.items()]
open_brl = [i['1a. open (BRL)'] for i in btc_list]
open_usd = [i['1b. open (USD)'] for i in btc_list]
high_brl = [i['2a. high (BRL)'] for i in btc_list]
high_usd = [i['2b. high (USD)'] for i in btc_list]
low_brl = [i['3a. low (BRL)'] for i in btc_list]
low_usd = [i['3b. low (USD)'] for i in btc_list]
close_brl = [i['4a. close (BRL)'] for i in btc_list]
close_usd = [i['4b. close (USD)'] for i in btc_list]
volume = [i['5. volume'] for i in btc_list]
market_cap_usd = [i['6. market cap (USD)'] for i in btc_list]

btc_dict = {'open(BRL)': open_brl, 'open(USD)': open_usd, 'high(BRL)': high_brl, 'high(USD)': high_usd, 'low(BRL)': low_brl, 
    'low(USD)': low_usd, 'close(BRL)': close_brl, 'close(USD)': close_usd, 'volume': volume, 'market cap (USD)': market_cap_usd}

# Bitcoin Price DataFrame
btc_df = pd.DataFrame(data=btc_dict, index=date_list)
btc_df.index = pd.to_datetime(btc_df.index)

today = date.today()
yesterday = today - timedelta(days=1)
day_before_yesterday = yesterday - timedelta(days=1)
yesterday = yesterday.strftime("%Y-%m-%d")
day_before_yesterday = day_before_yesterday.strftime("%Y-%m-%d")

# Yesterday's closing price
yesterday_price = btc_df['close(BRL)'][btc_df.index == yesterday].values[0]
# The day before yesterda'ys closing price
day_before_yesterday_price = btc_df['close(BRL)'][btc_df.index == day_before_yesterday].values[0]

# Fluctuation
difference = float(yesterday_price) - float(day_before_yesterday_price)
diff_percent = round(difference / float(yesterday_price)) * 100

# Get news and send email - If the variation is higher than 5
if abs(diff_percent) > 5:
    news_params = {
        'apiKey': API_KEY_NEWS,
        'qInTitle': ASSET_NEWS
    }

    news_response = requests.get(NEWS_API, params=news_params)
    articles = news_response.json()['articles'][:3]
    
    email = [f"Headline: {article['title']} \nBrief: {article['description']}" for article in articles]
    email.insert(0, 'Subject:Bitcoin message\n')
    email = '\n\n'.join(email)

    connection = smtplib.SMTP('smtp.gmail.com')
    connection.starttls()
    connection.login(user=FROM_EMAIL, password=EMAIL_PASSWORD)
    connection.sendmail(from_addr=FROM_EMAIL, to_addrs=TO_EMAIL, msg=email)
    connection.close()