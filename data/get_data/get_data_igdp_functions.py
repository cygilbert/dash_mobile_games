from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests


def get_soup_from_url(
        url="http://www.jeuxvideo.com/tous-les-jeux/machine-100/",
        parser='html.parser'):
    index = requests.get(url).text
    return BeautifulSoup(index, parser)


def get_dico_igdb_from_url_igdb(url_igdb):
    soup_igdb = get_soup_from_url(url_igdb)
    try:
        dico_infos = {
            el.text.split(':')[0].strip().lower():
                el.text.split(':')[1].strip()
            for el in soup_igdb.
                find('div', {'class': 'gamepage-tabs'}).find_all('p')
            if 'Genre' in el.text
        }
    except TypeError:
        dico_infos = {}
    dico_infos['url_igdb'] = url_igdb
    dico_infos['game'] = soup_igdb.find('h1').text
    dico_infos['release_date'] = soup_igdb\
        .find('h2', {'class': 'banner-subheading'}).text.strip()
    try:
        dico_infos['seller'] = soup_igdb\
            .find('h3', {'class': 'banner-subsubheading'}).text.strip()
    except TypeError:
        pass
    # href_age = f"/{
    #     url_igdb.replace('{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url_igdb)),'')
    # }/age_rating"
    # dico_infos['age_rating'] = {
    #     el.text.split()[0]: el.text
    #     for el in soup_igdb.find_all("a", {'href':href_age})
    # }
    store_div = soup_igdb\
        .find('div', {'class': 'gamepage-tabs'})\
        .findChildren('div', recursive=False)[1]
    links_store = [
        el['href'] for el in store_div
        .findChild('span', recursive=False).find_all('a')
        if ('itunes.apple' in el['href']) or 'play.google' in el['href']
    ]
    d_links_store = {
        '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(link)): link
        for link in links_store
    }
    dico_infos['links_store'] = d_links_store
    return dico_infos


def get_dico_google_from_url_google(url_google):
    soup_android = get_soup_from_url(url_google)
    dico_infos = {
        'mean_rating': soup_android
        .find('div', {'class': 'BHMmbe'}).text
    }
    dico_infos['n_rating'] = soup_android\
        .find('span', {'class': 'EymY4b'}).text
    try:
        dico_infos['price'] = soup_android\
            .find('span', {'class': 'oocvOe'}).find('button')['aria-label']
    except TypeError:
        pass
    dico_infos['seller'] = soup_android\
        .find('a', {'class': 'hrTbp R8zArc'}).text
    try:
        dico_infos['update'] = soup_android\
            .find('div', {'class': 'hAyfc'}).find('span').text
    except TypeError:
        pass
    return dico_infos


def get_dico_apple_from_url_apple(url_apple):
    soup_apple = get_soup_from_url(url_apple)
    infos = soup_apple\
        .find_all('div', {'class': 'information-list__item l-row'})
    dico_infos = {
        info.find('dt').text.lower(): info.find('dd').text.strip()
        for info in infos
        if info.find('dt').text in ['Seller', 'Compatibility', 'Price']
    }
    if 'iPhone' in dico_infos['compatibility']:
        dico_infos['mean_rating'] = soup_apple\
            .find(
                'span', {'class': 'we-customer-ratings__averages__display'}
            ).text
        dico_infos['n_rating'] = soup_apple\
            .find(
                'div', {
                    'class':
                    'we-customer-ratings__count small-hide medium-show'
                }
            ).text
        dico_infos.pop('compatibility', None)
        return dico_infos
    else:
        return


def get_dico_infos_from_url_igdb(url_igdb):
    try:
        dico_infos = get_dico_igdb_from_url_igdb(url_igdb)
        if 'https://itunes.apple.com/' in dico_infos['links_store']:
            try:
                dico_infos['apple'] =\
                    get_dico_apple_from_url_apple(
                        dico_infos['links_store']['https://itunes.apple.com/']
                    )
            except TypeError:
                pass
        if 'https://play.google.com/' in dico_infos['links_store']:
            try:
                dico_infos['google'] =\
                    get_dico_google_from_url_google(
                        dico_infos['links_store']['https://play.google.com/']
                    )
            except TypeError:
                pass
        return dico_infos
    except TypeError:
        return {'url_igdb': url_igdb}
