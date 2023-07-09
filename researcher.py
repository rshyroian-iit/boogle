import tiktoken
import time
import json
import tiktoken
import re
import os
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from utils.ai import embedding_function, cosine_similarity, turbo_boogle
from databases.google_search_thread import fetch_content_google, get_google_search_results
from databases.arxiv_search_thread import fetch_content_arxiv, get_arxiv_search_results
from databases.wikipedia_search_thread import fetch_content_wikipedia, get_wikipedia_search_results
from databases.reddit_search_thread import fetch_content_reddit, get_reddit_search_results
from databases.stackoverflow_search_thread import fetch_content_stack_overflow, get_stackoverflow_search_results
from utils.prompts import generate_search_prompt, generate_search_system_message
import tiktoken
import requests
model = "gpt-3.5-turbo"
enc = tiktoken.encoding_for_model(model)
cpu_count = min(32, 2 * os.cpu_count() + 4)

def scrape_resource(resource_id, db, bucket):
    start_time = time.time()
    print("Scraping resource")
    pages = []
    embeddings = []
    results = []
    favicon = ''
    db.collection('resources').document(resource_id).update({'status': 'pending'})
    status = 'pending'
    while status != 'complete':
        status = db.collection('resources').document(resource_id).get().to_dict()['status']
        time.sleep(1)
    resource = db.collection('resources').document(resource_id).get().to_dict()
    resource_path = resource['json_path']
    resource_name = resource['name']
    resource_link = resource['pdf_url']
    resource_json = json.loads(bucket.blob(resource_path).download_as_string())
    resource_pages = resource_json['pages']
    for page in resource_pages:
        pages.append(page['page_text'])
        embeddings.append(page['page_embedding'])
    if 'favicon' not in resource_json:
        resource_json['favicon'] = 'https://upload.wikimedia.org/wikipedia/commons/8/87/PDF_file_icon.svg'
        favicon = 'https://upload.wikimedia.org/wikipedia/commons/8/87/PDF_file_icon.svg'
    else:
        favicon = resource_json['favicon']
    order = 0
    for i in range(len(pages)):    
        results.append({'content': pages[i], 'embedding': embeddings[i], 'title': resource_name, 'similarity': 0, 'favicon': favicon, 'url': resource_link, 'order': order, 'snippet': '', 'source': 'Miscellaneous', 'time': time.time() - start_time})
    return results

def scrape_resources(resource_ids, db, bucket):
    print("Scraping resources")
    results = []
    # multithread this
    with ThreadPoolExecutor(max_workers = cpu_count) as executor:
        futures = []
        for resource_id in resource_ids:
            futures.append(executor.submit(scrape_resource, resource_id, db, bucket))
        for future in as_completed(futures):
            results += future.result()
            future.cancel()
        executor.shutdown(wait=False)
    return results

def split_content(content, length=800):
    content_tokens = enc.encode(content['content'].replace('<|endoftext|>', ''))
    if len(content_tokens) > length:
        reminder = len(content_tokens) % length
        division_result = len(content_tokens) // length
        length = length + reminder // division_result + 1
    content_chunks = [content_tokens[i:i+length] for i in range(0, len(content_tokens), length)]
    content_text_chunks = [{"text": enc.decode(chunk), "order": i} for i, chunk in enumerate(content_chunks)]
    content['chunks'] = content_text_chunks
    return content

def max_cosine_similarity(search_query_embeddings, content_embedding):
    max_similarity = 0
    for search_query_embedding in search_query_embeddings:
        similarity = cosine_similarity(search_query_embedding, content_embedding)
        if similarity > max_similarity:
            max_similarity = similarity
    return max_similarity

def get_list_of_search_results(query):
    if query['source'] == 'Google':
        return get_google_search_results(query['query'])
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

def get_html_content_from_search_result(result):
    if 'url' in result:
        url = result['url']
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.text
        except requests.exceptions.RequestException as err:
            print("Error occurred: ", err)
    return None

def get_list_of_results(query, number_of_retries=0):
    start_time = time.time()
    resource_ids = []
    search_options = search_options = {'google': True, 'wikipedia': True, 'arxiv': True,
                          'stackoverflow': True, 'reddit': True, 'miscellaneous': True}
    
    #doc = db.collection('chats').document(doc_id).get().to_dict()
    #resource_ids = doc['resource_ids']
    #search_options = doc['search_options']

    #db.collection('chats').document(doc_id).update({'user_update': 'Searching for relevant content...'})
    # if all values are false, then set all values to true
    if not any(search_options.values()):
        search_options = {'google': True, 'wikipedia': True, 'arxiv': True,
                          'stackoverflow': True, 'reddit': True, 'miscellaneous': True}
    search_queries = []
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
            return get_list_of_results(query, number_of_retries + 1)
        else:
            return None
    if search_queries_str != '':
        search_queries = search_queries_str.split("\n")
        search_queries = [search_query.strip().replace('"', '').replace("'", '') for search_query in search_queries if search_query.strip()]
    '''
    search_queries.append(f"Google {query}")
    
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
            google_search_queries.append(query)
            all_search_queries.append({'source': 'Google', 'query': query})
        elif search_query.strip().startswith("Arxiv"):
            query = search_query.strip()[5:].strip()
            if query.startswith("{") and query.endswith("}"):
                query = re.sub(r'^\{+|\}+$', '', query)
            arxiv_search_queries.append(query)
            all_search_queries.append({'source': 'Arxiv', 'query': query})
        elif search_query.strip().startswith("Wikipedia"):
            query = search_query.strip()[9:].strip()
            if query.startswith("{") and query.endswith("}"):
                query = re.sub(r'^\{+|\}+$', '', query)
            wikipedia_search_queries.append(query)
            all_search_queries.append({'source': 'Wikipedia', 'query': query})
        elif search_query.strip().startswith("StackOverflow"):
            query = search_query.strip()[13:].strip()
            if query.startswith("{") and query.endswith("}"):
                query = re.sub(r'^\{+|\}+$', '', query)
            stackoverflow_search_queries.append(query)
            all_search_queries.append({'source': 'StackOverflow', 'query': query})
        elif search_query.strip().startswith("Reddit"):
            query = search_query.strip()[6:].strip()
            if query.startswith("{") and query.endswith("}"):
                query = re.sub(r'^\{+|\}+$', '', query)
            reddit_search_queries.append(query)
            all_search_queries.append({'source': 'Reddit', 'query': query})
        else:
            query = search_query.strip()
            if query.startswith("{") and query.endswith("}"):
                query = re.sub(r'^\{+|\}+$', '', query)
            miscellaneous_search_queries.append(query)
            all_search_queries.append({'source': 'Miscellaneous', 'query': query})
    content_results = []
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
    content_results = results
    print(len(content_results), 'done with all')
    snippets_token_count = 0
    for i in range(len(content_results)):
        print(i)
        print(content_results[i]['url'])
        print(content_results[i]['title'])
        print(content_results[i]['source'])
        snippets_token_count += get_token_count(content_results[i]['snippet'])
        print(get_token_count(content_results[i]['snippet']))
        print("\n")
    print("snippets token count: ", snippets_token_count)

    unique_urls = []
    unique_content_results = []
    for content_result in content_results:
        if content_result['url'] not in unique_urls:
            unique_urls.append(content_result['url'])
            unique_content_results.append(content_result)

    results = []
    #response_list.append({"url": key, "match": int(round(sum(searches_by_links[key]['top_5_similarities']) / len(searches_by_links[key]['top_5_similarities']), 2) * 100), "icon": searches_by_links[key]['content'][0]['favicon'], "title": searches_by_links[key]['content'][0]['title'].strip(), "content": [], "tokens": 0, "snippet": searches_by_links[key]['content'][0]['snippet'], "urls": [], "chat": []})
    with ThreadPoolExecutor(max_workers = cpu_count) as executor:
        futures = [executor.submit(extract_content_from_search_result, content_result) for content_result in unique_content_results]
        for future in futures:
            if future is not None:
                results.append(future.result())
            future.cancel()
        executor.shutdown(wait=False)
    content_results = results

    content_results = [result for result in content_results if not result['content'].startswith('Error:')]

    if len(content_results) == 0 and len(resource_ids) == 0:
        if number_of_retries < 3:
            messages = [{'role': 'system', 'content': "All you are capable of is providing a reworded version of the users input. You are not capable of producing dialogue."},
                        {'role': 'user', 'content': f"Output a reworded version of: {query}. Output nothing else. Reworded version: "}]
            new_query = turbo_boogle(messages=messages, model=model, max_tokens=120).strip()
            return get_list_of_results(new_query, number_of_retries + 1)
        else:
            return None
        
    for i in range(len(content_results)):
        print(i)
        print(content_results[i]['url'].strip())
        print(content_results[i]['title'].strip())
        print(content_results[i]['source'])
        print(content_results[i]['time'])
        print(get_token_count(content_results[i]['content']))
        print("\n")

    print("done with all")
    print("time taken: ", time.time() - start_time)
        
    results = []
    with ThreadPoolExecutor(max_workers = cpu_count) as executor:
        futures = [executor.submit(split_content, content_result) for content_result in content_results]
        for future in futures:
            results.append(future.result())
            future.cancel()
        executor.shutdown(wait=False)
    print("done with splitting")

    '''
    print("starting the embedding process")
    search_queries.append(query)
    search_query_embeddings = []
    with ThreadPoolExecutor(max_workers = cpu_count) as executor:
        futures = [executor.submit(embedding_function, search_query) for search_query in search_queries]
        for future in futures:
            search_query_embeddings.append(future.result())
            future.cancel()
        executor.shutdown(wait=False)

    if len(search_query_embeddings) == 0:
        if number_of_retries < 3:
            messages = [{'role': 'system', 'content': "All you are capable of is providing a reworded version of the users input. You are not capable of producing dialogue."},
                        {'role': 'user', 'content': f"Output a reworded version of: {query}. Output nothing else. Reworded version: "}]
            new_query = turbo_boogle(messages=messages, model=model, max_tokens=120).strip()
            return get_list_of_results(new_query, number_of_retries + 1)
        else:
            return None

    with ThreadPoolExecutor(max_workers = 100) as executor:
        futures = [executor.submit(
            embedding_function, split_content_result['content']) for split_content_result in split_content_results]
        for future in futures:
            index = futures.index(future)
            split_content_results[index]['embedding'] = future.result()
            split_content_results[index]['similarity'] = max_cosine_similarity(search_query_embeddings, split_content_results[index]['embedding'])
            future.cancel()
        executor.shutdown(wait=False)
    print("ending the embedding process")
    '''

    '''
    if len(resource_ids) > 0:
        resource_results = scrape_resources(resource_ids, db, bucket)
        for resource_result in resource_results:
            resource_result['similarity'] = max_cosine_similarity(
                search_query_embeddings, resource_result['embedding'])
        split_content_results += resource_results
    '''
    print("NUMBER OF RESULTS: " + str(len(results)))
    '''
    if len(split_content_results) == 0:
        if number_of_retries < 3:
            messages = [{'role': 'system', 'content': "All you are capable of is providing a reworded version of the users input. You are not capable of producing dialogue."},
                        {'role': 'user', 'content': f"Output a reworded version of: {query}. Output nothing else. Reworded version: "}]
            new_query = turbo_boogle(messages=messages, model=model, max_tokens=120).strip()
            return get_list_of_results(new_query, number_of_retries + 1)
        else:
            return None
    '''
    print("done with all")
    print("time taken: ", time.time() - start_time)
    for i in range(len(results)):
        results[i]['tokens'] = get_token_count(results[i]['content'])
    results = [result for result in results if result['tokens'] > 100]
    research = json.dumps(results)
    with open(f'research/research{timestamp}.json', 'w') as f:
        f.write(research)
    f.close()

    return results

'''
def search(query, timestamp):
    #query_embedding = embedding_function(query)
    split_content_results = get_list_of_results(query)
    if split_content_results is None:
        return "Say sorry studyhub's server is overloaded, please try again later."
    searches_by_links = {}
    for result in split_content_results:
        result['content'] = result['content'].strip()
        result['content'] = re.sub(r'\s\s+', ' ', result['content'])
        result['content'] = re.sub(r'\n\s*\n', '\n\n', result['content'])
        result['content'] = re.sub(r'-\s*\n', '-', result['content'])
        if result['url'] not in searches_by_links:
            searches_by_links[result['url']] = {"content": [], "top_5_similarities": []}
        searches_by_links[result['url']]['content'].append(result)
    
    for key in searches_by_links:
        searches_by_links[key]['content'] = sorted(searches_by_links[key]['content'], key=lambda x: x['similarity'], reverse=True)
        for content in searches_by_links[key]['content'][:5]:
            searches_by_links[key]['top_5_similarities'].append(content['similarity'])

    response_list = []
    for key in searches_by_links:
        response_list.append({"url": key, "match": int(round(sum(searches_by_links[key]['top_5_similarities']) / len(searches_by_links[key]['top_5_similarities']), 2) * 100), "icon": searches_by_links[key]['content'][0]['favicon'], "title": searches_by_links[key]['content'][0]['title'].strip(), "content": [], "tokens": 0, "snippet": searches_by_links[key]['content'][0]['snippet'], "urls": [], "chat": []})
        content_token_count = 0
        contents = searches_by_links[key]['content']
        contents = sorted(contents, key=lambda x: x['order'])
        for content in contents:
            response_list[-1]['content'].append({"order": content['order'], "text": content['content'], "embedding": content['embedding']})
            content_token_count += len(enc.encode(content['content']))
        response_list[-1]['tokens'] = content_token_count
        response_list[-1]['chat'] = [{"role": "user", "content": f"Instructions: Answer my question while also providing context about the website. It's vital you use Markdown in order to ensure that your response is highly interpretable and organized. Use headers to categorize your response, lists to provide readability, and bold to signify importance.\nQuery: {query}\nResponse: ", "embedding": query_embedding, "summary": "Provide an overview"}]
        #response_list[-1]['chat'] = [{"role": "user", "content": query, "embedding": query_embedding, "summary": query}]
    response_list = sorted(response_list, key=lambda x: x['match'], reverse=True)
    response_list = [response for response in response_list if response['tokens'] > 100]
    research = json.dumps(response_list)
    with open(f'research/research{timestamp}.json', 'w') as f:
        f.write(research)
    f.close()
    #os.remove(f'research{timestamp}.json')
    file_name = f'research/research{timestamp}.json'
    return file_name

'''
if __name__ == '__main__':
    query = "Global Warming"
    timestamp = time.time()
    get_list_of_results(query)
    #search(query, timestamp)



'''
resulting research json format:
{
    [
        {
            "url": "https://www.nature.com/articles/s41558-020-0694-0",
            "match": 100,
            "icon": "https://www.nature.com/articles/s41558-020-0694-0",
            "title": "The effects of climate change on global agricultural production",
            "snippet": "The effects of climate change on global agricultural production are likely to be substantial and are expected to increase over time. The effects of ...",
            "content": [
                {"order": 2, text: "The effects of climate change on global agricultural", "embedding": "[0.88, 0.32, ..., 0.03]"},
                {"order": 2, text: "production are likely to be substantial and are expected to increase over time.", "embedding": "[0.88, 0.32, ..., 0.03]"},
                {"order": 2, text: "The effects of climate change on global agricultural production are likely to be", "embedding": "[0.88, 0.32, ..., 0.03]"},
                {"order": 2, text: "substantial and are expected to increase over time. The effects of climate change", "embedding": "[0.88, 0.32, ..., 0.03]"}, 
                {"order": 2, text: "on global agricultural production are likely to be substantial and are expected to increase over time. The effects of climate", "embedding": "[0.88, 0.32, ..., 0.03]"},
                {"order": 2, text: "change on global agricultural production are likely to be substantial and are expected to increase over time. The effects of", "embedding": "[0.88, 0.32, ..., 0.03]"},
                {"order": 2, text: "climate change on global agricultural production are likely to be substantial and are expected to increase over time. The effects of", "embedding": "[0.88, 0.32, ..., 0.03]"},
                {"order": 2, text: "climate change on global agricultural production are likely to be substantial and are expected to increase over time.", "embedding": "[0.88, 0.32, ..., 0.03]"}
            ]
            chat: [
                {"role": "system", "content": "You are able to address the research question. Try to also include some quotes and paraphrases. Your response should be: 1. Concise and informative: The response is to be broken down into clear and concise statements, allowing readers to grasp the key points quickly without excessive detail or jargon. 2. Structured and organized: The answer is structured into main sections with markdown headers, each addressing one aspect of the question. Sub-points under each section are organized in a bulleted list format, making it easy to read and understand. 3. Neutral and objective: The answer it to present both positive and negative aspects, highlighting the duality of the topic without taking sides or providing personal opinions. 4. Factual and supported: Each point made in the response is to be based on factual information and supported by provided source and examples when possible. This approach ensures the response maintains a high level of accuracy and trustworthiness."},
                {"role": "user", "content": "What are the effects of climate change on global agricultural production?", "embedding": "[0.88, 0.32, ..., 0.03]", "summary": "Effects of climate change on global agricultural production"},
            ]
        },
        {
            "url": "https://www.nature.com/articles/s41558-020-0694-0",
            "match": 100,
            "icon": "https://www.nature.com/articles/s41558-020-0694-0",
            "title": "The effects of climate change on global agricultural production",
            "snippet": "The effects of climate change on global agricultural production are likely to be substantial and are expected to increase over time. The effects of ...",
            "content": [
                {"order": 2, text: "The effects of climate change on global agricultural", "embedding": "[0.88, 0.32, ..., 0.03]"},
                {"order": 2, text: "production are likely to be substantial and are expected to increase over time.", "embedding": "[0.88, 0.32, ..., 0.03]"},
                {"order": 2, text: "The effects of climate change on global agricultural production are likely to be", "embedding": "[0.88, 0.32, ..., 0.03]"},
                {"order": 2, text: "substantial and are expected to increase over time. The effects of climate change", "embedding": "[0.88, 0.32, ..., 0.03]"}, 
                {"order": 2, text: "on global agricultural production are likely to be substantial and are expected to increase over time. The effects of climate", "embedding": "[0.88, 0.32, ..., 0.03]"},
                {"order": 2, text: "change on global agricultural production are likely to be substantial and are expected to increase over time. The effects of", "embedding": "[0.88, 0.32, ..., 0.03]"},
                {"order": 2, text: "climate change on global agricultural production are likely to be substantial and are expected to increase over time. The effects of", "embedding": "[0.88, 0.32, ..., 0.03]"},
                {"order": 2, text: "climate change on global agricultural production are likely to be substantial and are expected to increase over time.", "embedding": "[0.88, 0.32, ..., 0.03]"}
            ]
            chat: [
                {"role": "system", "content": "You are able to address the research question. Try to also include some quotes and paraphrases. Your response should be: 1. Concise and informative: The response is to be broken down into clear and concise statements, allowing readers to grasp the key points quickly without excessive detail or jargon. 2. Structured and organized: The answer is structured into main sections with markdown headers, each addressing one aspect of the question. Sub-points under each section are organized in a bulleted list format, making it easy to read and understand. 3. Neutral and objective: The answer it to present both positive and negative aspects, highlighting the duality of the topic without taking sides or providing personal opinions. 4. Factual and supported: Each point made in the response is to be based on factual information and supported by provided source and examples when possible. This approach ensures the response maintains a high level of accuracy and trustworthiness."},
                {"role": "user", "content": "What are the effects of climate change on global agricultural production?", "embedding": "[0.88, 0.32, ..., 0.03]", "summary": "Effects of climate change on global agricultural production"},
            ]
        },
    ]
}
'''
