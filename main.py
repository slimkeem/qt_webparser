import requests
from bs4 import BeautifulSoup
import time


def __extract_features(big_table_row, small_table_row):
    article_id = big_table_row.get('id')

    try:
        author = small_table_row.find(class_='hnuser').string
    except Exception as ex:
        author = 'not_defined'

    try:
        points = small_table_row.find(class_='score').string
    except Exception as ex:
        points = '0 points'

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
        'rank': big_table_row.span.string
    }

    return article_info


def extract_features(page):
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/53.0.2785.143 Safari/537.36'}
    url = 'https://news.ycombinator.com/'

    resp = requests.get(f'{url}{page}', headers=headers, timeout=10)
    output_list = []

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'html5lib')
        tr_blocks = soup.find_all('tr', class_='athing')
        print(len(tr_blocks))
        smaller_tr_blocks = soup.find_all('td', class_='subtext')

        for index, tr in enumerate(tr_blocks):
            output_list.append(__extract_features(tr, smaller_tr_blocks[index]))

        return output_list


if __name__ == '__main__':
    required_pages = ['news', 'ask', 'show']
    collated_output_list = []

    for page in required_pages:
        collated_output_list += extract_features(page)
        time.sleep(0.25)

    print(collated_output_list)
