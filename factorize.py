from multiprocessing import Pool, cpu_count
import logging
from time import time

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)


def worker(number):
    ''' тупий перебор, просто щоб заміряти час'''
    result = []
    for i in range(1, number+1):
        if not number % i:
            result.append(i)
    return result

def factorize_single(*numbers):
    ''' приймає список чисел та повертає список чисел, 
    на які числа з вхідного списку поділяються без залишку (один процес)'''
    return [worker(number) for number in numbers]


def factorize_multi(*numbers):
    ''' приймає список чисел та повертає список чисел, 
    на які числа з вхідного списку поділяються без залишку (кілька процесів)'''
    final_list = []
    with Pool(processes=cpu_count()) as pool:
        for result in pool.map(worker, numbers):
            # logger.debug(result)
            final_list.append(result)
    return final_list


test_list = [128, 255, 99999, 10651060, 1986980, 10567576, 10567570, 1293847]

logger.debug('Старт в 1 процес')
timer = time()
single = factorize_single(*test_list)
logger.debug(f'\nРезультат: {time() - timer}')

logger.debug(f'\nСтарт в {cpu_count()} процеси')
timer = time()
multi  = factorize_multi(*test_list)
logger.debug(f'Результат: {time() - timer}')

# assert a == [1, 2, 4, 8, 16, 32, 64, 128]
# assert b == [1, 3, 5, 15, 17, 51, 85, 255]
# assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
# assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]
print([ll for ll in single])
print([ll for ll in multi])
print(f'\033[94m Результати обчислень однакові: \033[92m {single == multi} \033[0m')
