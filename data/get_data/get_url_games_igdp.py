from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
import pickle
import time


def verbose_counter_print(page_counter, verbose_counter, n_pages, start):
    duration = time.time() - start
    mean_duration = duration / page_counter
    estimation_until_last = ((n_pages - page_counter) * mean_duration)
    print(f'{page_counter} iters in {duration:.1f} s, \
{mean_duration:.1f} s per pages, \
end estimated in {estimation_until_last:.1f} s')


def get_url_games(game, time_sleep=2):
    try:
        if_media = (game.get_attribute('class') != 'media overflow')
    except StaleElementReferenceException:
        time.sleep(time_sleep)
        if_media = (game.get_attribute('class') != 'media overflow')
    if if_media:
        try:
            return game.find_element_by_tag_name('a').get_attribute('href')
        except StaleElementReferenceException:
            time.sleep(time_sleep)
            return game.find_element_by_tag_name('a').get_attribute('href')


def get_href_from_platform_allgames(
        url='https://www.igdb.com/platforms/ios/games',
        time_sleep=2,
        verbose_counter=50,
        n_pages=None):
    driver = webdriver.Firefox()
    # get web page
    driver.get(url)
    if not(n_pages):
        n_pages = int(
          driver.find_element_by_class_name('pagination')
          .find_elements_by_tag_name('span')[-2].text
        )
    page_counter = 1
    urls_game = []
    start = time.time()
    while True:
        games = driver\
          .find_element_by_class_name('game-list-container')\
          .find_elements_by_class_name('media')
        urls_game += list(
          filter(
            None, [get_url_games(game, time_sleep) for game in games]
          )
        )
        page_counter += 1
        if verbose_counter and (page_counter % verbose_counter == 0):
            verbose_counter_print(
              page_counter, verbose_counter, n_pages, start
            )
        if page_counter > n_pages:
            break
        driver\
            .find_element_by_class_name('next')\
            .find_element_by_tag_name('span')\
            .click()
        time.sleep(time_sleep)
    print(f'finished {page_counter} iters in {(time.time()-start):.1f}')
    return urls_game


def get_url_games_igdp(
      repo_save='',
      n_pages=None,
      verbose_counter=50,
      time_sleep=2):
    urls_games = []
    for os in ['ios', 'android']:
        print(os)
        url = f'https://www.igdb.com/platforms/{os}/games'
        urls_games += get_href_from_platform_allgames(
            url=url,
            n_pages=n_pages,
            verbose_counter=verbose_counter,
            time_sleep=time_sleep
        )
    urls_games = list(dict.fromkeys(urls_games))
    pik_urls_games = repo_save + 'data_games.dat'
    pickle.dump(urls_games, open(pik_urls_games, 'wb'))


if __name__ == "__main__":
    get_url_games_igdp(n_pages=6, verbose_counter=2, time_sleep=2)
