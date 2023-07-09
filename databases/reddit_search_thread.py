import praw
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
client_id = 'cUxXFdL21ImtfcBKH-En-w'
client_secret = '2e8jaMb-3nclThb0Jahv7CnCI1DwBw'
user_agent = 'Patrick Mauboussin personal use script'
username = 'studyhubai'
password = 'SWxuz9H44!7!dUP'
reddit_instance = praw.Reddit(client_id=client_id,
                                client_secret=client_secret,
                                user_agent=user_agent,
                                username=username,
                                password=password)

def get_reddit_search_results(query, limit=8):
    try:
        results = []
        for submission in reddit_instance.subreddit('all').search(query, sort='relevance', time_filter='all', limit=limit):
            results.append({
                'snippet': submission.selftext,
                'url': f"https://www.reddit.com{submission.permalink}",
                'favicon': 'https://www.redditstatic.com/desktop2x/img/favicon/favicon-32x32.png',
                'title': submission.title,
                'source': 'Reddit'
            })
        return results
    except Exception as e:
        print(f'Error getting Reddit search results: {e}')
        return []

def fetch_content_reddit(result):
    time_start = time.time()
    url = result['url']
    reddit_id = url.split('/')[-3]
    submission = reddit_instance.submission(id=reddit_id)
    comments = ''
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        comments += comment.body
    if comments == '':
        print(f'Error fetching content from {url} in {time.time() - time_start} seconds')
        return {
            'content': 'Error: No comments found',
            'url': result['url'],
            'favicon': result['favicon'],
            'title': result['title'],
            'snippet': result['snippet'],
            'source': result['source'],
            'time': time.time() - time_start
        }
    else:
        print(f'Fetched content from {url} in {time.time() - time_start} seconds')
        return {
            'content': comments,
            'url': result['url'],
            'favicon': result['favicon'],
            'title': result['title'],
            'snippet': result['snippet'],
            'source': result['source'],
            'time': time.time() - time_start
        }

if __name__ == '__main__':
    results = get_reddit_search_results('python', 5)
    for result in results:
        print(result['title'])
        print(result['url'])
        print('\n')
