import requests
from databases.user_agents import get_random_header
from concurrent.futures import ThreadPoolExecutor, as_completed
import pdfplumber
import requests
import time
from io import BytesIO

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def fetch_content_arxiv(result):
    title = result['title']
    snippet = result['snippet']
    url = result['url']
    favicon = result['favicon']
    time_start = time.time()
    try:
        user_agent = get_random_header()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            pdf_data = BytesIO(response.content)
            text = extract_text_from_pdf(pdf_data)
            print(f'Fetched content from {url} in {time.time() - time_start} seconds')
            return {'url': url, 'content': text, 'favicon': favicon, 'title': title, 'snippet': snippet, 'source': 'Arxiv', 'time': time.time() - time_start}
        else:
            #print(f'Error fetching content from {url}: Status code {response.status_code}')
            print(f'Error fetching content from {url} in {time.time() - time_start} seconds')
            return {'url': url, 'content': f'Error: Status code {response.status_code}', 'favicon': None, 'title': title, 'snippet': snippet, 'source': 'Arxiv', 'time': time.time() - time_start}
    except Exception as e:
        #print(f'Error fetching content from {url}: {e}')
        print(f'Error fetching content from {url} in {time.time() - time_start} seconds')
        return {'url': url, 'content': f'Error: {e}', 'favicon': None, 'title': title, 'snippet': snippet, 'source': 'Arxiv', 'time': time.time() - time_start}


def get_arxiv_search_results(search_term, max_results=10):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    print("SEARCH TERM: " + search_term)
    search_results = search_arxiv(search_term, max_results)
    if search_results.startswith('Error: '):
        print("ERROR")
        return []
    import xml.etree.ElementTree as ET
    root = ET.fromstring(search_results)

    links = []

    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.replace('\n', ' ')
        paper_id = entry.find('{http://www.w3.org/2005/Atom}id').text
        print("LOOK HERE")
        paper_id = paper_id.replace("http://arxiv.org/abs/", "http://arxiv.org/pdf/")
        paper_id = paper_id + ".pdf"
        print("PAPER ID: " + paper_id)
        links.append({'url': paper_id, 'title': title, 'snippet': summary, 'favicon': "https://static.arxiv.org/static/browse/0.3.4/images/icons/favicon-32x32.png", 'source': 'Arxiv'})
    return links

def search_arxiv(search_term, max_results=10):
    base_url = 'http://export.arxiv.org/api/query'
    search_query = f'search_query=all:{search_term}&start=0&max_results={max_results}'
    url = f'{base_url}?{search_query}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return f'Error: {response.status_code}'