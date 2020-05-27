import pickle
import pandas as pd
import re
import datetime
import pathlib
from get_data_functions import get_soup_from_url


# Build big companie
def get_big_companies(DATA_PATH):
    soup_big_companies = get_soup_from_url(
      'https://newzoo.com/insights/rankings/top-25-companies-game-revenues/'
    )
    rows_big_companies = soup_big_companies\
        .find('table', {'class': 'rankingtable first'})\
        .find('tbody')\
        .find_all('tr')[:-2]
    big_companies = [
      row.find_all('td')[1].text.strip().replace('*', '')
      for row in rows_big_companies
    ]
    big_companies.remove('EA')
    big_companies.append('ELECTRONIC ARTS')
    big_companies.sort()
    pickle.dump(big_companies, open(DATA_PATH.joinpath('companies.dat'), 'wb'))
    return big_companies


def get_big_seller(row, big_companies):
    for company in big_companies:
        company_low = company.strip().lower()
        for seller_type in ['seller', 'apple_seller', 'google_seller']:
            if isinstance(row[seller_type], str):
                # if (company_low == 'ea') and \
                #   (similar(row[seller_type].lower(), company_low) > 0.95):
                #    return company
                if ((row[seller_type].lower()) in company_low)\
                  or (company_low in (row[seller_type].lower())):
                    return company
    return


def preprocess_rating_view(dico, store='google'):
    try:
        mean_rating = float(dico['mean_rating'].replace(',', '.'))
        if store == 'google':
            n_rating = int(re.sub('[^0-9]', '', dico['n_rating']))
        else:
            x = dico['n_rating']
            n_rating = int(
                1000 * float(re.sub('[^0-9.]', '', x)) if 'K' in x
                else float(re.sub('[^0-9.]', '', x))
            )
        return mean_rating, int(n_rating)
    except (TypeError, KeyError):
        return


def parse_date(string):
    try:
        string = string.replace('st', '').replace('nd', '')\
            .replace('rd', '').replace('th', '').replace(',', '')
    except AttributeError:
        return
    try:
        string = datetime.datetime.strptime(string, '%d %b %Y')
    except ValueError:
        string = string.split('-')[0]
        string = datetime.datetime.strptime(string, '%Y')
    return string


def get_seller_store(dico_store):
    try:
        return dico_store['seller']
    except ValueError:
        return


def unfold_genres(row_genres):
    try:
        return [
          {'index genre': row_genres['index'], 'Genre': genre}
          for genre in row_genres['genre split']
        ]
    except TypeError:
        return


def preprocess_data(DATA_PATH, data_in, data_out):
    # Open data
    games = pickle.load(open(data_in, 'rb'))
    df_game = pd.DataFrame(games).reset_index()
    df_game.loc[:, 'Release date'] = df_game['release_date'].map(parse_date)
    # Store
    for store in ['apple', 'google']:
        df_game.loc[:, f'{store}_seller'] =\
            df_game[store].map(get_seller_store)
    # Get company
    df_editor = df_game[['seller', 'apple_seller', 'google_seller']]
    big_companies = get_big_companies(DATA_PATH)
    df_game.loc[:, 'Company'] = df_editor\
        .apply(get_big_seller, args=(big_companies,), axis=1)
    df_game[~df_game['Company'].isnull()].groupby('Company').size()
    print(df_game.shape)
    # Get genre
    df_game['genre'] = df_game['genre'].fillna('Unknow')
    df_game['genre split'] =\
        df_game['genre'].dropna().map(lambda x: x.split(', '))
    genres = list(
      set(
        [
          item for sublist in list(df_game['genre split'].dropna())
          for item in sublist
        ]
      )
    )
    genres.sort()
    pickle.dump(genres, open(DATA_PATH.joinpath('genres.dat'), 'wb'))
    games_genre = list(df_game.apply(unfold_genres, axis=1).dropna())
    df_games_genre = pd.DataFrame(
      [
        item for sublist in games_genre
        for item in sublist
      ]
    )
    df_games_genre.to_csv(DATA_PATH.joinpath('games_genre.csv'), index=False)
    # Final preprocess
    df_save = df_game[['game', 'Release date', 'Company', 'genre']]\
        .rename(columns={'game': 'Game'})
    df_save = df_save[~df_save['Game'].isnull()]
    df_final = []
    for store in ['apple', 'google']:
        # rating and n_rating
        df_pp = df_game[store].apply(
            preprocess_rating_view, args=(store,)
        )\
            .apply(pd.Series)\
            .rename(columns={0: 'Mean Note', 1: 'Number of Vote'}).dropna()
        df_pp['Number of Vote'] = df_pp['Number of Vote'].apply(int)
        df_store = df_save.merge(df_pp, left_index=True, right_index=True)
        df_store['store'] = store
        df_final.append(df_store)
    df_final = pd.concat(df_final).rename(columns={'genre': 'Genres'})
    df_final.to_csv(DATA_PATH.joinpath(data_out))


if __name__ == "__main__":
    # Data path
    PATH = pathlib.Path('__file__').parent
    DATA_PATH = PATH.joinpath('../').resolve()
    preprocess_data(
      DATA_PATH,
      data_in='data_games.dat',
      data_out='df_mobile_games.csv'
    )
