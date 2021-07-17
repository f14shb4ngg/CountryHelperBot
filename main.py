import json
import requests
import telebot
from datetime import datetime

bot = telebot.TeleBot('')  # telegram token


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello! Send me the name of the country in English.")


@bot.message_handler(content_types=['text'])
def request(message):
    bot.send_message(message.chat.id, "Please, give me a few seconds.")
    country_name = message.text
    url1 = f'https://restcountries.eu/rest/v2/name/{country_name}'
    url2 = f'https://travelbriefing.org/{country_name}?format=json'
    response1 = requests.get(url1)
    response2 = requests.get(url2)
    if response1.status_code != 200 or response2.status_code != 200:
        bot.send_message(message.chat.id,
                         "Can not find enough information about that country, "
                         "make sure that you entered the right name of the country.")
        return
    country_info1 = json.loads(response1.content)
    country_info2 = json.loads(response2.content)
    full_name = country_info2['names']['full']
    capital = country_info1[0]['capital']
    region = country_info1[0]['region']
    population = country_info1[0]['population']
    ISO2 = country_info2['names']['iso2'].lower()
    Alpha2 = country_info1[0]['alpha2Code'].lower()
    if ISO2 != Alpha2:
        bot.send_message(message.chat.id,
                         "Can not find enough information about that country, "
                         "make sure that you entered the right name of the country.")
        return
    flag = f'https://flagcdn.com/w2560/{ISO2}.png'
    flag_response = requests.get(flag)
    if flag_response.status_code != 200:
        bot.send_message(message.chat.id,
                         "Can not find enough information about that country, "
                         "make sure that you entered the right name of the country.")
        return
    languages = [lang['language'] for lang in country_info2['language']]
    languages_string = ", ".join(languages)
    currency_name = country_info2['currency']['name']
    borders = [border['name'] for border in country_info2['neighbors']]
    borders_string = ", ".join(borders)
    UNIX = message.date
    yesterday = datetime.utcfromtimestamp(UNIX - 86400).strftime('%Y-%m-%d')
    before_yesterday = datetime.utcfromtimestamp(UNIX - 86400 * 2).strftime('%Y-%m-%d')
    corona_url = f'https://api.covid19api.com/country/{country_name}' \
                 f'?from={before_yesterday}T00:00:00Z&to={yesterday}T00:00:00Z'
    corona_response = requests.get(corona_url)
    if corona_response.status_code != 200:
        bot.send_message(message.chat.id,
                         "Can not find enough information about that country, "
                         "make sure that you entered the right name of the country.")
        return
    corona_info = json.loads(corona_response.content)
    new_confirmed = corona_info[1]['Confirmed'] - corona_info[0]['Confirmed']
    total_confirmed = corona_info[1]['Confirmed']
    total_deaths = corona_info[1]['Deaths']
    bot.send_message(message.chat.id, f'Full name: {full_name}\nCapital: {capital}\nRegion: {region}\
    \nApproximate population: {population}\nLanguages: {languages_string}\nBorders: {borders_string}\
    \nCurrency: {currency_name}\nFlag: {flag}\nCoronavirus information:\nTotal cases: {total_confirmed}\
    \nTotal deaths: {total_deaths}\nNew cases: {new_confirmed}')


bot.polling()
