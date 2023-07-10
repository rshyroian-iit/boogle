import tiktoken
import time
import json
import tiktoken
import re
import os
from concurrent.futures import ThreadPoolExecutor
from utils.ai import turbo_boogle
from databases.google_search_thread import fetch_content_google, get_google_search_results
from databases.arxiv_search_thread import fetch_content_arxiv, get_arxiv_search_results
from databases.wikipedia_search_thread import fetch_content_wikipedia, get_wikipedia_search_results
from databases.reddit_search_thread import fetch_content_reddit, get_reddit_search_results
from databases.stackoverflow_search_thread import fetch_content_stack_overflow, get_stackoverflow_search_results
from utils.prompts import generate_search_system_message, generate_search_prompt
import tiktoken
from generate_queries import get_search_queries
import validators
model = "gpt-3.5-turbo"
enc = tiktoken.encoding_for_model(model)
cpu_count = min(32, 2 * os.cpu_count() + 4)

def get_list_of_search_results(query):
    if query['source'] == 'Google':
        num_results = query['query'][-2:]
        if num_results == '00':
            num_results = '0'
        query['query'] = query['query'][:-3]
        return get_google_search_results(query['query'], num_results)
    elif query['source'] == 'Arxiv':
        return get_arxiv_search_results(query['query'])
    elif query['source'] == 'Wikipedia':
        return get_wikipedia_search_results(query['query'])
    elif query['source'] == 'StackOverflow':
        return get_stackoverflow_search_results(query['query'])
    elif query['source'] == 'Reddit':
        return get_reddit_search_results(query['query'])
    else:
        return []

def extract_content_from_search_result(result):
    if result['source'] == 'Google':
        return fetch_content_google(result)
    elif result['source'] == 'Arxiv':
        return fetch_content_arxiv(result)
    elif result['source'] == 'Wikipedia':
        return fetch_content_wikipedia(result)
    elif result['source'] == 'StackOverflow':
        return fetch_content_stack_overflow(result)
    elif result['source'] == 'Reddit':
        return fetch_content_reddit(result)
    else:
        return None

def get_token_count(text):
    return len(enc.encode(text))

def search_url(url, timestamp):
    display_queries = [url]
    result = {'url': url, 'content': '', 'favicon': url, 'title': url, 'snippet': url, 'source': 'Google', 'time': 0.0, 'data': ''}
    result = extract_content_from_search_result(result)
    result['tokens'] = get_token_count(result['content'])
    result['chat'] = []
    result['processed'] = False
    results = [result]
    results = [result for result in results if not result['content'].startswith('Error:')]
    results = [result for result in results if result['tokens'] > 100]
    json_object = {}
    json_object['queries'] = display_queries
    json_object['results'] = results
    research = json.dumps(json_object, indent=4)
    with open(f'research/research{timestamp}.json', 'w') as f:
        f.write(research)
    f.close()
    return f'research/research{timestamp}.json'


def search(query, timestamp, number_of_retries=0):
    if query.startswith("http://") or query.startswith("https://"):
        if validators.url(query):
            return search_url(query, timestamp)

    start_time = time.time()
    search_options = search_options = {'google': True, 'wikipedia': True, 'arxiv': True,
                          'stackoverflow': True, 'reddit': True, 'miscellaneous': True}
    if not any(search_options.values()):
        search_options = {'google': True, 'wikipedia': True, 'arxiv': True,
                          'stackoverflow': True, 'reddit': True, 'miscellaneous': True}
    additonal_search_queries = []
    #additonal_search_queries = get_search_queries(query)
    display_queries = []
    search_queries = []
    #search_queries.insert(0,query)
    '''
    search_queries_str = ''
    system_message = generate_search_system_message(search_options)
    prompt = generate_search_prompt(search_options, query)
    try:
        messages = [{'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': prompt}]
        search_queries_str = turbo_boogle(messages=messages, model=model, max_tokens=120).strip()
    except Exception as e:
        search_queries_str = ''
    if search_queries_str == '':
        if number_of_retries < 3:
            return search(query, timestamp, number_of_retries + 1)
        else:
            return None
    if search_queries_str != '':
        search_queries = search_queries_str.split("\n")
        search_queries = [search_query.strip().replace('"', '').replace("'", '') for search_query in search_queries if search_query.strip()]
    '''
    search_queries.append(query)
    search_queries += additonal_search_queries
    search_queries = list(set(search_queries))
    #Add Google{ before every element in search queries and } after
    for i in range(len(search_queries)):
        search_queries[i] = 'Google{' + search_queries[i] + '}'

    print(search_queries)
    all_search_queries = []
    stackoverflow_search_queries = []
    google_search_queries = []
    arxiv_search_queries = []
    wikipedia_search_queries = []
    reddit_search_queries = []
    miscellaneous_search_queries = []
    for search_query in search_queries:
        if search_query.strip().startswith("Google"):
            query = search_query.strip()[6:].strip()
            if query.startswith("{") and query.endswith("}"):
                query = re.sub(r'^\{+|\}+$', '', query)
                if query in display_queries:
                    continue
                display_queries.append(query)
            google_search_queries.append(query + "+00")
            google_search_queries.append(query + "+10")
            google_search_queries.append(query + "+20")
            all_search_queries.append({'source': 'Google', 'query': query + "+00"})
            all_search_queries.append({'source': 'Google', 'query': query + "+10"})
            all_search_queries.append({'source': 'Google', 'query': query + "+20"})
            #all_search_queries.append({'source': 'Google', 'query': query})
        elif search_query.strip().startswith("Arxiv"):
            query = search_query.strip()[5:].strip()
            if query.startswith("{") and query.endswith("}"):
                query = re.sub(r'^\{+|\}+$', '', query)
                display_queries.append(query)
            arxiv_search_queries.append(query)
            all_search_queries.append({'source': 'Arxiv', 'query': query})
        elif search_query.strip().startswith("Wikipedia"):
            query = search_query.strip()[9:].strip()
            if query.startswith("{") and query.endswith("}"):
                query = re.sub(r'^\{+|\}+$', '', query)
                display_queries.append(query)
            wikipedia_search_queries.append(query)
            all_search_queries.append({'source': 'Wikipedia', 'query': query})
        elif search_query.strip().startswith("StackOverflow"):
            query = search_query.strip()[13:].strip()
            if query.startswith("{") and query.endswith("}"):
                query = re.sub(r'^\{+|\}+$', '', query)
                display_queries.append(query)
            stackoverflow_search_queries.append(query)
            all_search_queries.append({'source': 'StackOverflow', 'query': query})
        elif search_query.strip().startswith("Reddit"):
            query = search_query.strip()[6:].strip()
            if query.startswith("{") and query.endswith("}"):
                query = re.sub(r'^\{+|\}+$', '', query)
                display_queries.append(query)
            reddit_search_queries.append(query)
            all_search_queries.append({'source': 'Reddit', 'query': query})
        else:
            query = search_query.strip()
            if query.startswith("{") and query.endswith("}"):
                query = re.sub(r'^\{+|\}+$', '', query)
                display_queries.append(query)
            miscellaneous_search_queries.append(query)
            all_search_queries.append({'source': 'Miscellaneous', 'query': query})
    print("google queries", len(google_search_queries))
    print("arxiv queries", len(arxiv_search_queries))
    print("wikipedia queries", len(wikipedia_search_queries))
    print("reddit queries", len(reddit_search_queries))
    print("stackoverflow queries", len(stackoverflow_search_queries))
    print("miscellaneous queries", len(miscellaneous_search_queries))
    print("all queries", all_search_queries)
    results = []
    with ThreadPoolExecutor(max_workers = cpu_count) as executor:
        futures = [executor.submit(get_list_of_search_results, all_search_query) for all_search_query in all_search_queries]
        for future in futures:
            results += future.result()
            future.cancel()
        executor.shutdown(wait=False)
    unique_urls = []
    unique_content_results = []
    for content_result in results:
        if content_result['url'] not in unique_urls:
            unique_urls.append(content_result['url'])
            unique_content_results.append(content_result)

    results = []
    with ThreadPoolExecutor(max_workers = cpu_count) as executor:
        futures = [executor.submit(extract_content_from_search_result, content_result) for content_result in unique_content_results]
        for future in futures:
            if future is not None:
                results.append(future.result())
            future.cancel()
        executor.shutdown(wait=False)

    results = [result for result in results if not result['content'].startswith('Error:')]
    
    for i in range(len(results)):
        results[i]['tokens'] = get_token_count(results[i]['content'])
        results[i]['chat'] = []
        results[i]['processed'] = False
    results = [result for result in results if result['tokens'] > 100]
    json_object = {}
    json_object['queries'] = display_queries
    json_object['results'] = results
    research = json.dumps(json_object, indent=4)
    with open(f'research/research{timestamp}.json', 'w') as f:
        f.write(research)
    f.close()

    for i in range(len(results)):
        print(i)
        print(results[i]['url'].strip())
        print(results[i]['title'].strip())
        print(results[i]['snippet'].strip())
        print(results[i]['time'])
        print(results[i]['tokens'])
        print("\n")
    print("done with splitting")
    print("NUMBER OF RESULTS: " + str(len(results)))
    print("done with all")
    print("time taken: ", time.time() - start_time)
    return f'research/research{timestamp}.json'

if __name__ == '__main__':
    query = "Global Warming"
    timestamp = time.time()
    search(query, timestamp)