import operator

import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd


def __extract_features(big_table_row, small_table_row):
    article_id = big_table_row.get('id')

    try:
        author = small_table_row.find(class_='hnuser').string
    except Exception as ex:
        author = 'not_defined'

    try:
        points = int(small_table_row.find(class_='score').string.split()[0])
    except Exception as ex:
        points = 0

    comments_n = small_table_row.find_all(href=f'item?id={article_id}')[-1].string
    if 'comments' in comments_n:
        non_num_index = comments_n.find('comment')
        comments_n = comments_n[:non_num_index].split()[0] + " comments"
    else:
        comments_n = '0 comments'

    article_info = {
        'Headline': big_table_row.find(class_='titlelink').string,
        'Points': points,
        'Author': author,
        'Age': small_table_row.find(class_='age').string,
        'Comments': comments_n,
        'rank': int(float(big_table_row.span.string))
    }

    return article_info


def extract_features(page):
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/53.0.2785.143 Safari/537.36'}
    url = 'https://news.ycombinator.com/'

    resp = requests.get(f'{url}{page}', headers=headers, timeout=10)
    output_list = []

    max_thread = 30

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'html5lib')
        tr_blocks = soup.find_all('tr', class_='athing')
        smaller_tr_blocks = soup.find_all('td', class_='subtext')

        threads = min(max_thread, len(tr_blocks))

        with ThreadPoolExecutor(max_workers=threads) as executor:
            output_list = executor.map(__extract_features, tr_blocks, smaller_tr_blocks)

        # for index, tr in enumerate(tr_blocks):
        #     output_list.append(__extract_features(tr, smaller_tr_blocks[index]))

        return output_list


if __name__ == '__main__':
    required_pages = ['news', 'ask', 'show']
    collated_output_list = []

    for page in required_pages:
        collated_output_list += extract_features(page)
        time.sleep(0.25)

    collated_output_list.sort(key=operator.itemgetter('rank'))
    collated_output_list.sort(key=operator.itemgetter('Points'), reverse=True)

    keys = list(collated_output_list[0].keys())
    # print(keys)

    output_df = pd.DataFrame(collated_output_list)
    output_df.drop(['rank'], axis=1, inplace=True)
    output_df.to_csv('hacker_news2.csv')
