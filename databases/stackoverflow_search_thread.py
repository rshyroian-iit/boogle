import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

client_id = '26355'
client_secret = 'wkgVod8UWM4RfyOa0bmP8Q(('
key = '8hmuF)yi62jT2*8PG60Uhg(('

def get_stackoverflow_search_results(query, limit=5):
    url = 'https://api.stackexchange.com/2.2/search/advanced'
    headers = {
        'Accept-Encoding': 'gzip'
    }
    params = {
        'order': 'desc',
        'sort': 'relevance',
        'q': query,
        'site': 'stackoverflow',
        'key': key,
        'pagesize': limit,
        'filter': 'withbody'  # to get the body of the question
    }

    response = requests.get(url, headers=headers, params=params)
    results = response.json()

    formatted_results = []
    for item in results['items']:
        print(item['question_id'])
        soup = BeautifulSoup(item['body'], 'html.parser')  # parse HTML of question
        question = soup.get_text()  # convert to plain text
        #content = fetch_content(item['question_id'])
        formatted_results.append({
            #'content': content,
            'url': item['link'],
            'favicon': 'https://cdn.sstatic.net/Sites/stackoverflow/Img/favicon.ico?v=ec617d715196',
            'title': item['title'],
            'snippet': question,
            'source': 'StackOverflow',
        })
    return formatted_results

def fetch_content_stack_overflow(result):
    
    start_time = time.time()
    question_id = result['url'].split('/')[-2]
    print(question_id)
    url = f'https://api.stackexchange.com/2.2/questions/{question_id}/answers'
    headers = {
        'Accept-Encoding': 'gzip'
    }
    params = {
        'order': 'desc',
        'sort': 'votes',
        'site': 'stackoverflow',
        'key': key,
        'pagesize': 1,
        'filter': 'withbody'
    }

    response = requests.get(url, headers=headers, params=params)
    results = response.json()

    if results['items']:
        print(f'Fetched content from {url} in {time.time() - start_time} seconds')
        soup = BeautifulSoup(results['items'][0]['body'], 'html.parser')
        answer = soup.get_text()
        return {
            'content': answer,
            'url': result['url'],
            'favicon': result['favicon'],
            'title': result['title'],
            'snippet': result['snippet'],
            'source': result['source'],
            'time': time.time() - start_time
        }
    else:
        print(f'Error fetching content from {url} in {time.time() - start_time} seconds')
        return {
            'content': 'Error: No answer found',
            'url': result['url'],
            'favicon': result['favicon'],
            'title': result['title'],
            'snippet': result['snippet'],
            'source': result['source'],
            'time': time.time() - start_time
        }
    
if __name__ == '__main__':
    results = get_stackoverflow_search_results('python', limit=5)
    for result in results:
        print(result['title'])
        print(result['url'])
        print('\n')