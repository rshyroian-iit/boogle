
import json
from utils.ai import cosine_similarity, turbo_boogle, embedding_function, get_token_count
from utils.prompts import generate_chat_system_message, generate_keyword_prompt
from researcher import search
model = "gpt-3.5-turbo-16k"

def show_results(json_object):
    for i in range(len(json_object)):
        print(f"{i}. URL: " + json_object[i]["url"])
        print("TITLE: " + json_object[i]["title"].strip())
        print("SNIPPET: " + json_object[i]["snippet"].strip()[:200])
        print("MATCH: " + str(json_object[i]["match"]))
        print("TOKENS: " + str(json_object[i]["tokens"]))
        print("\n")

def generate_keywords(website):
    token_count = 0
    messages = []
    system_message = generate_keyword_prompt(website['url'], website['title'])
    messages.append({'role': 'system', 'content': system_message})
    for i in range (len(website['chat'])-1, -1, -1):
        token_count += get_token_count(website['chat'][i]['content'])
        if token_count > 2000:
            break
        message = {'role': website['chat'][i]['role'], 'content': website['chat'][i]['content']}
        messages.insert(0, message)
    # WE DO NEED THE MESSAGE (MODIFIED) BELOW BECAUSE IT ACTUALLY GENERATES A RESPONSE INSTEAD OF THE KEYWORDS
    messages.append({'role': 'user', 'content': 'List of keywords:'})
    keywords = turbo_boogle(messages=messages, model=model)
    return keywords # u here? it just gave a perfect response

def respond(website):
    keywords = generate_keywords(website)
    keywords_embedding = embedding_function(keywords)
    website['content'].sort(key=lambda x: cosine_similarity(x['embedding'], keywords_embedding), reverse=True)
    print("#### keywords: " + keywords)
    relevant_text = []
    token_count = 0
    for i in range(len(website['content'])):
        if token_count + get_token_count(website['content'][i]['text']) > 5500:
            continue
        relevant_text.append(website['content'][i]['text'])
        token_count += get_token_count(website['content'][i]['text'])
    relevant_text_str = '\n'.join(relevant_text)
    system_message = generate_chat_system_message(relevant_text_str, website['url'], website['title'])
    messages = []
    messages.append({'role': 'system', 'content': system_message})
    token_count = get_token_count(system_message)
    print("#### token count: " + str(token_count))
    for i in range (len(website['chat'])-1, -1, -1):
        token_count += get_token_count(website['chat'][i]['summary'])
        if token_count > 8000:
            break
        message = {'role': website['chat'][i]['role'], 'content': website['chat'][i]['summary']}
        messages.insert(0, message)
    response = turbo_boogle(messages=messages, model=model, max_tokens=1200)
    system_message = "Your only job is to summarize any input provided to you."
    messages = [{'role': 'system', 'content': system_message},
                {'role': 'user', 'content': response}]
    summary = turbo_boogle(messages=messages, model=model, max_tokens=200)
    website['chat'].append({'role': 'assistant', 'content': response, 'summary': summary})

def chatWithWebsite(website):
    print("#### " + website['title'])
    for message in website['chat']:
        print(message['role'] + ": " + message['content'])
    while True:
        if website['chat'][-1]['role'] == 'user':
            respond(website)
            print("#### " + website['chat'][-1]['role'] + ": " + website['chat'][-1]['content'])
        else:
            message = input("user: ")
            if message == "exit":
                break
            system_message = "Your only job is to summarize any input provided to you."
            messages = [{'role': 'system', 'content': system_message},
                        {'role': 'user', 'content': message}]
            summary = turbo_boogle(messages=messages, model=model, max_tokens=200)
            website['chat'].append({'role': 'user', 'content': message, 'summary': summary})
            

if __name__ == '__main__':
    search_query = input("Search query: ")
    json_file = search(search_query)
    json_object = json.load(open(json_file))
    while True:
        print("#### Total results: " + str(len(json_object)))
        show_results(json_object)
        print("#### Pick the result you want to open: ")
        index = int(input())
        if index == -1:
            break
        if index >= len(json_object):
            print("#### Invalid index")
            continue
        website = json_object[index]
        print('\n')
        chatWithWebsite(website)
        print('\n')
