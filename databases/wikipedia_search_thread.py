import requests
from databases.user_agents import get_random_header
from concurrent.futures import ThreadPoolExecutor, as_completed
import html2text
import requests
import time

def fetch_content_wikipedia(result):
    snippet = result['snippet']
    url = result['url']
    favicon_url = result['favicon']
    title = result['title']
    time_start = time.time()
    try:
        user_agent = get_random_header()
        headers = {
            'User-Agent': user_agent
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            html_string = response.text
            extractor = html2text.HTML2Text()
            html2text_text = extractor.handle(html_string)
            print(f'Fetched content from {url} in {time.time() - time_start} seconds')
            return {'url': url, 'content': html2text_text, 'favicon': favicon_url, 'title': title, 'snippet': snippet, 'source': 'Wikipedia', 'time': time.time() - time_start}
        else:
            #print(f'Error fetching content from {url}: Status code {response.status_code}')
            print(f'Error fetching content from {url} in {time.time() - time_start} seconds')
            return {'url': url, 'content': f'Error: Status code {response.status_code}', 'favicon': favicon_url, 'title': title, 'snippet': snippet, 'source': 'Wikipedia', 'time': time.time() - time_start}
    except Exception as e:
        #print(f'Error fetching content from {url}: {e}')
        print(f'Error fetching content from {url} in {time.time() - time_start} seconds')
        return {'url': url, 'content': f'Error: {e}', 'favicon': favicon_url, 'title': title, 'snippet': snippet, 'source': 'Wikipedia', 'time': time.time() - time_start}

def get_wikipedia_search_results(query, limit=5):
    params = {
        'action': 'query',
        'generator': 'search',
        'gsrsearch': query,
        'gsrlimit': limit,
        'prop': 'extracts',
        'exintro': 1,
        'explaintext': 1,
        'format': 'json',
        'utf8': 1,
        'formatversion': 2,
    }
    
    base_url = 'https://en.wikipedia.org/w/api.php'
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    pages_data = []
    try:
        pages_data = response.json()['query']['pages']
    except Exception as e:
        print(f'Error getting Wikipedia search results: {e}')
        print(response.json())
        return []
    
    results = []
    for page in pages_data:
        if 'missing' not in page:
            # print all keys in page
            for key in page:
                print(key)
            print(page['pageid'])
            print(page['ns'])
            print(page['index'])
            results.append({
                'snippet': page['extract'],
                'url': f"https://en.wikipedia.org/?curid={page['pageid']}",
                'favicon': "https://en.wikipedia.org/static/favicon/wikipedia.ico",
                'title': page['title'],
                'source': 'Wikipedia'
            })
    return results

if __name__ == '__main__':
    print(get_wikipedia_search_results('Chinatown San Francisco', 1))