from get_data_igdp_functions import get_dico_infos_from_url_igdb
from multiprocessing import Pool
import pickle
import random
import time
import os


def main(parallelize=False):
    pik_all = 'all_games.dat'
    all_games = pickle.load(open(pik_all, 'rb'))
    random.shuffle(all_games)
    # all_games = all_games[:50]
    if parallelize:
        # Create a pool of workers to execute processes
        n_cpu = os.cpu_count()
        print(n_cpu)
        pool = Pool(processes=n_cpu)
        start = time.time()
        # Map (service, tasks), applies function to each partition
        output = pool.map(get_dico_infos_from_url_igdb, all_games)
        pool.close()
        pool.join()
        end = time.time()
        print(f'{end - start} seconds elapsed.')
    else:
        check_counter = 10
        n_games = len(all_games)
        random.shuffle(all_games)
        output = []
        start = time.time()
        print("C'est parti")
        for games_counter, url_igdb in enumerate(all_games):
            output.append(get_dico_infos_from_url_igdb(url_igdb))
            if games_counter % check_counter == 0 and games_counter > 0:
                duration = time.time() - start
                mean_duration = duration / games_counter
                estimation_until_last = (
                    (n_games - games_counter) * mean_duration
                )
                print(
                    f'{games_counter} iter in {duration}, {mean_duration} per games,\
                    end estimated in {estimation_until_last}'
                )
        print(
            f'{games_counter} iter in {duration}, {mean_duration} per games,\
            end estimated in {estimation_until_last}'
        )
    pik_game = 'data_games2.dat'
    pickle.dump(output, open(pik_game, 'wb'))


if __name__ == "__main__":
    # execute only if run as a script
    main(parallelize=True)
