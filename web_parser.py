import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd


def __extract_features(big_table_row, small_table_row):
    """
    This function uses some html elements to search for the key information we need

    :param big_table_row: The main row which contains the news topic and its link
    :param small_table_row: The smaller row under the main row which contains some meta information about the news
    topic such as author etc.
    :return: a dictionary object holding the key information we need.
    """

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
    """
    This function calls __extract_features asynchronously. It downloads the web page it is given and gets all the
    html elements, and then passes selected elements to __extract_features for extraction.
    :param page: Page is the current page which it is working on
    :return: Returns a Pandas DataFrame object of the dictionaries of desired information.
    """

    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/53.0.2785.143 Safari/537.36'}
    url = 'https://news.ycombinator.com/'

    resp = requests.get(f'{url}{page}', headers=headers, timeout=10)

    max_thread = 32

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'html5lib')
        tr_blocks = soup.find_all('tr', class_='athing')
        smaller_tr_blocks = soup.find_all('td', class_='subtext')

        threads = min(max_thread, len(tr_blocks))

        with ThreadPoolExecutor(max_workers=threads) as executor:
            output_list = executor.map(__extract_features, tr_blocks, smaller_tr_blocks)

        output_df = pd.DataFrame(output_list)

        return output_df


def run_parser(list_pages):
    """
    This function passes a number of desired pages for extraction of features asynchronously. It then sorts the
    information gotten back
    :param list_pages: A list of desired pages which will be sent to extract_features to append the base url and extract
    information
    :return: returns the sorted final Pandas Dataframe containing desired information from web all pages.
    """

    threads = len(list_pages)
    with ThreadPoolExecutor(max_workers=threads) as executor:
        collated_output_list = executor.map(extract_features, list_pages)

    gens = [internal_gen for internal_gen in collated_output_list]
    output_df = pd.concat(gen for gen in gens)

    output_df = output_df.sort_values(['Points', 'rank'], ascending=[False, True])
    return output_df


if __name__ == '__main__':
    required_pages = ['news', 'ask', 'show']

    final_output = run_parser(required_pages)

    # can drop the rank of the info before converting to csv if desired by uncommenting the next line.
    # final_output.drop(['rank'], axis=1, inplace=True)

    # for converting pandas DF to csv.
    final_output.to_csv('hacker_news3.csv', index=False)
