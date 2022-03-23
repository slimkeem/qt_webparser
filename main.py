import requests
from bs4 import BeautifulSoup
import time


def extract_features(page):
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/53.0.2785.143 Safari/537.36'}
    url = 'https://news.ycombinator.com/'

    resp = requests.get(f'{url}{page}', headers=headers, timeout=10)
    output_list = []

    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, 'html5lib')
        tr_blocks = soup.find_all('tr', class_='athing')
        smaller_tr_blocks = soup.find_all('td', class_='subtext')

        for index, tr in enumerate(tr_blocks):
            article_id = tr.get('id')

            try:
                author = smaller_tr_blocks[index].find(class_='hnuser').string
            except Exception as ex:
                author = 'not_defined'

            try:
                points = soup.find(id=f'score_{article_id}').string
                comments_n = smaller_tr_blocks[index].find_all(href=f'item?id={article_id}')[1].string
                if comments_n != "discuss":
                    non_num_index = comments_n.find('comment')
                    comments_n = comments_n[:non_num_index].split()[0] + " comments"
                else:
                    comments_n = '0 comments'
            except Exception as ex:
                points = '0 points'

            article_info = {
                'Headline': tr.find(class_='titlelink').string,
                'Points': points,
                'Author': author,
                'Age': smaller_tr_blocks[index].find(class_='age').string,
                'Comments': comments_n,
                'rank': tr.span.string
            }
            output_list.append(article_info)

        return output_list


if __name__ == '__main__':
    required_pages = ['news', 'ask', 'show']
    collated_output_list = []

    for page in required_pages:
        output_list = extract_features(page)
        collated_output_list += output_list
        time.sleep(0.25)

    print(collated_output_list)
