import requests
from bs4 import BeautifulSoup


if __name__ == '__main__':
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/53.0.2785.143 Safari/537.36'}
    html = None
    links = None

    url = 'https://news.ycombinator.com/'

    r = requests.get(url, headers=headers, timeout=10)

    if r.status_code == 200:
        html = r.text
        soup = BeautifulSoup(html, 'html5lib')

        available_pages = soup.select('a', href=True)
        required_pages = ['news', 'ask', 'show']

        links = [url + page['href'].strip() for page in available_pages if page['href'] in required_pages]

        #     for page in available_pages:
        #         if page["href"] in required_pages:
        #             if 'http' not in page['href']:
        #                 link = url+page["href"]
        #             else:
        #                 link = page["href"]
        #             links.append(link.strip())
        print(links)
