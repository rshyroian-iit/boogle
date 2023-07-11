
from googleapiclient.discovery import build
from databases.user_agents import get_random_header
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
import pdfplumber
import html2text
import re
import requests
from bs4 import BeautifulSoup
import time
my_api_key = "AIzaSyCZb4DUfEVpnDKQHOX5fVsWo1J_eI-AnN0"
my_cse_id = "e452fb13d362947d0"

def extract_title_and_text_from_pdf(pdf_data, default_title):
    with pdfplumber.open(pdf_data) as pdf:
        metadata = pdf.metadata
        title = metadata.get('Title', default_title)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return title, text

def fetch_content_google(result):
    time_start = time.time()
    url = result['url']
    snippet = result['snippet']
    favicon_url = result['favicon']
    default_title = result['title']
    try:
        user_agent = get_random_header()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers, timeout=1)
        html_string = response.text
        if response.status_code == 200:
            if url.endswith('.pdf'):
                pdf_data = BytesIO(response.content)
                title, text = extract_title_and_text_from_pdf(pdf_data, default_title)
                print(f'Fetched content from {url} in {time.time() - time_start} seconds')
                response_content_str = response.content.decode('utf-8')
                return {'url': url, 'content': text, 'favicon': favicon_url, 'title': title, 'snippet': snippet, 'source': 'Google', 'time': time.time() - time_start, 'data': response_content_str}
            extractor = html2text.HTML2Text()
            html2text_text = extractor.handle(html_string)
            html2text_text = re.sub(r'(\w)-(\s|\n)*', r'\1-', html2text_text) 
            match = re.search('<title>(.*?)</title>', html_string, re.IGNORECASE)
            title = match.group(1) if match else default_title
            if title.strip() == '':
                title = default_title
            # remove all lines before the first occurrence of the title
            #html2text_text = new_html2text_text
            #html2text_text = fix_markdown(html2text_text)
            #with open(f'speed_test/{title}.md', 'w') as f:
            #    f.write(html2text_text)
            #f.close()
            print(f'Fetched content from {url} in {time.time() - time_start} seconds')
            return {'url': url, 'content': html2text_text, 'favicon': favicon_url, 'title': title, 'snippet': snippet, 'source': 'Google', 'time': time.time() - time_start, 'data': response.text}
        else:
            #print(f'Error fetching content from {url}: Status code {response.status_code}')
            print(f'Error fetching content from {url} in {time.time() - time_start} seconds')
            return {'url': url, 'content': f'Error: Status code {response.status_code}', 'favicon': favicon_url, 'title': default_title, 'snippet': snippet, 'source': 'Google', 'time': time.time() - time_start, 'data': response.text}
    except Exception as e:
        #print(f'Error fetching content from {url}: {e}')
        print(f'Error fetching content from {url} in {time.time() - time_start} seconds')
        return {'url': url, 'content': f'Error: {e}', 'favicon': favicon_url, 'title': default_title, 'snippet': snippet, 'source': 'Google', 'time': time.time() - time_start, 'data': ''}

def get_google_search_results(query, num_results=0):
    from requests_html import HTMLSession
    import requests
    url = f"https://www.google.com/search?q=" + query + f"&start={num_results}"
    try:
        session = HTMLSession()
        response = session.get(url)
        session.close()
    except requests.exceptions.RequestException as e:
        print(e)
        return []
    print(response.html)
    responses = response.html.find('.MjjYud')
    results = []
    for result in responses:
        snippet = result.find('.VwiC3b', first=True)
        url = result.find('.yuRUbf', first=True)
        favicon = result.find('.XNo5Ab', first=True)
        title = result.find('.LC20lb', first=True)
        if url is None:
            continue
        else:
            try:
                url = url.find('a', first=True).attrs['href']
            except:
                print('url error')
                continue
        if favicon is None:
            favicon = 'https://www.google.com/favicon.ico'
        else:
            try:
                favicon = favicon.find('img', first=True).attrs['src']
            except:
                favicon = 'https://www.google.com/favicon.ico'
                print('favicon error')
        if snippet is None:
            snippet = 'Could not extract snippet'
        else:
            try:
                snippet = snippet.text
            except:
                snippet = 'Could not extract snippet'
                print('snippet error')
        if title is None:
            title = 'Untitled'
        else:
            try:
                title = title.text
            except:
                title = 'Could not extract title'
                print('title error')
        results.append({
            'snippet': snippet,
            'url': url,
            'favicon': favicon,
            'title': title,
            'source': 'Google'
        })
    return results

if __name__ == '__main__':
    results = get_google_search_results('how to make a website')
    for result in results:
        print("URL" + result['url'])
        print("TITLE" + result['title'])
        print("SNIPPET" + result['snippet'])
        print("FAVICON" + result['favicon'])
        print("\n")