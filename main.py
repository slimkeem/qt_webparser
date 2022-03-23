import requests
from bs4 import BeautifulSoup
import time


if __name__ == '__main__':
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/53.0.2785.143 Safari/537.36'}
    BASE_URL = 'https://news.ycombinator.com/'
    required_pages = ['news', 'ask', 'show']
    output_list = []

    for page in required_pages:
        resp = requests.get(f'{BASE_URL}{page}', headers=headers, timeout=10)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html5lib')
            tr_blocks = soup.find_all('tr', class_='athing')
            smaller_tr_blocks = soup.find_all('td', class_='subtext')

            for index, tr in enumerate(tr_blocks):
                article_id = tr.get('id')
                age = smaller_tr_blocks[index].find(class_='age').string
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
                    'Age': age,
                    'Comments': comments_n,
                    'rank': tr.span.string
                }
                output_list.append(article_info)
            time.sleep(0.5)
    print(output_list[80])
