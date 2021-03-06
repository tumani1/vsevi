# coding: utf-8

""" Поиск трансляций championat.com """

import re
from bs4 import BeautifulSoup
from django.utils import timezone
from crawler.tor import simple_tor_get_page

TRANSLATION_URL = 'http://www.championat.com'


def parse_translation_championat_com():
    translation_list = []
    champ_dict = {}

    # Get page
    list_translations_page = simple_tor_get_page(TRANSLATION_URL+'/broadcast/')
    list_translations_soup = BeautifulSoup(list_translations_page)

    championship_bloc = list_translations_soup.find('div', {'class': 'broadcast__menu'})

    #Create championship map
    for champ in championship_bloc.find_all('div', {'class': 'broadcast__menu__i'}):
        try:
            img = champ.find('div', {'class': 'broadcast__tournament'})
            if img:
                champ_dict[img.get('class')[-1]] = champ.p.text
        except Exception, e:
            print e.message

    translation_tables = list_translations_soup.find_all('table', {'class': 'table broadcast__table'})

    for table in translation_tables:
        for trans in table.find_all('tr', {'class': 'broadcast__table__i'}):
            try:

                # Get current year
                current_year = timezone.now().year

                # Get title
                title_tag = trans.find('td', {'class': 'broadcast__table__title _title'})
                title = title_tag.text

                # Get date and time
                dates = trans.find_all('td', {'class': None})
                for td in dates:
                    if td.findChildren():
                        dates.remove(td)
                date = re.findall(ur'\d+', dates[0].text)
                time = re.findall(ur'\d+', dates[1].text)

                #Get price
                price_tag = trans.find('div', {'class': '_paid'})
                price = re.search(ur'\d+', price_tag.text).group()

                #Get link
                link_tag = trans.find('a', {'class': 'broadcast__table__link'})
                link = TRANSLATION_URL + link_tag.get('href')

                #Get championship
                championship_img = trans.find('td', {'class': '_icon'}).div.get('class')
                championship = champ_dict[championship_img[-1]]

                #Get value from translation page
                trans_page = simple_tor_get_page(link)
                trans_soup = BeautifulSoup(trans_page)
                value_div = trans_soup.find('div', {'class': 'broadcast'})
                value = value_div.iframe.get('src')

                #Create dict with information about translation
                translation_data = {
                    'title': title,
                    'date': timezone.datetime(year=current_year, month=int(date[1]), day=int(date[0]), hour=int(time[0]),
                                              minute=int(time[1])),
                    'price': float(price),
                    'link': link,
                    'meta': {'championship': championship if championship else None},
                    'value': value,
                }
                translation_list.append(translation_data)
            except Exception, e:
                print e.message

    return translation_list