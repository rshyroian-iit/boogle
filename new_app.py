from boost_query import get_boosted_query
from search import search
import json
from io import BytesIO
from PIL import Image
import streamlit as st
import base64
from utils.ai import cosine_similarity, turbo_boogle, get_token_count, embedding_function
from utils.prompts import generate_chat_system_message, generate_keyword_prompt
import time
import concurrent.futures
from markdown import markdown
from datetime import datetime, timedelta
import tiktoken
import re
import os
#from google_embeddings import embedding_function
from generate_quick_response import get_quick_response
from vertex_test import handle_chat
from website_pairings import website_pairs
import streamlit.components.v1 as components
enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
model = "gpt-3.5-turbo-16k"
st.set_page_config(layout="wide", page_title="Readability")
css = '''
<style>
section.main > div:has(~ footer ) {
    padding-bottom: 5px;
}
</style>
'''
st.markdown(css, unsafe_allow_html=True)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
# Load the websites_by_category dictionary from the JSON file
with open('websites_by_category.json', 'r') as f:
    websites_by_category = json.load(f)

# Create a dictionary to store the state of each checkbox
checkbox_states = {}


if 'object' not in st.session_state:
    st.session_state['object'] = None
if 'selected_time' not in st.session_state:
    st.session_state['selected_time'] = 'default'
if 'query' not in st.session_state:
    st.session_state['query'] = ''
if 'search_websites' not in st.session_state:
    st.session_state['search_websites'] = None
if 'selected_website' not in st.session_state:
    st.session_state['selected_website'] = None
if 'timestamp' not in st.session_state:
    st.session_state['timestamp'] = None
if 'results_error' not in st.session_state:
    st.session_state['results_error'] = None
if 'model_settings' not in st.session_state:
    st.session_state['model_settings'] = {'model': 'chat-bison@001', 'temperature': 0.2, 'token_count': 250, 'top_p': 0.8, 'top_k': 40}
if 'readability_view' not in st.session_state:
    st.session_state['readability_view'] = True
if 'quick_response' not in st.session_state:
    st.session_state['quick_response'] = None
if 'time_options' not in st.session_state:
    st.session_state["time_options"] = ["Any Time", "Past Hour", "Past Day",
                        "Past Week", "Past Month", "Past Year"]
if 'reader_view' not in st.session_state:
    st.session_state['reader_view'] = True
 
def update_quick_response(query, snippets):
    print(snippets)
    st.session_state['quick_response'] = get_quick_response(query, snippets)

    
def update_query(query):
   # print('updating query')
    st.session_state['query'] = query
    print('query: ', query)
    
def pil_to_b64(image, format="PNG"):
    buff = BytesIO()
    image.save(buff, format=format)
    img_str = base64.b64encode(buff.getvalue()).decode("utf-8")
    return img_str


def find_matching_parentheses(md_content, i):
    opening_square_bracket_index = -1
    closing_parentheses_index = -1
    closing_square_bracket_count = 1
    opening_parentheses_count = 1
    for j in range(1, i+1):
        if md_content[i-j] == ']':
            closing_square_bracket_count += 1
        elif md_content[i-j] == '[':
            closing_square_bracket_count -= 1
            if closing_square_bracket_count == 0:
                opening_square_bracket_index = i-j
                break
    for k in range(i+2, len(md_content)):
        if md_content[k] == '(':
            opening_parentheses_count += 1
        elif md_content[k] == ')':
            opening_parentheses_count -= 1
            if opening_parentheses_count == 0:
                closing_parentheses_index = k
                break
    return opening_square_bracket_index, closing_parentheses_index

def remove_nested_newlines(md_content):
    i = 0
    while i < len(md_content) - 1:
        if md_content[i] == ']' and md_content[i+1] == '(':
            j, k = find_matching_parentheses(md_content, i)
            if j != -1 and k != -1:
                brackets_content = md_content[j+1:i]
                parentheses_content = md_content[i+2:k]
                brackets_content = brackets_content.replace('\n', ' ')
                parentheses_content = parentheses_content.replace('\n', ' ').replace(' ', '')
                md_content = md_content[:j+1] + brackets_content + md_content[i: i+2] + parentheses_content + md_content[k:]
                i = j + len(brackets_content) + 2 + len(parentheses_content) + 1
        i += 1
    return md_content

def remove_lines_inbetween(md_content):
    result = ""
    is_inside = False
    runnung_string = ""
    for i in range(len(md_content)):
        if md_content[i] == "]":
            is_inside = True
            result += md_content[i]
        elif md_content[i] == "(":
            is_inside = False
            result += md_content[i]
            runnung_string = ""
        else:
            if md_content[i].strip() == "" and is_inside:
                runnung_string += md_content[i]
            else:
                if is_inside:
                    result += runnung_string + md_content[i]
                else:
                    result += md_content[i]
                is_inside = False
                runnung_string = ""
    return result
        

def remove_trash(md_content):
    # remove all tines that don't start with # and have only one word
    lines = md_content.split('\n')
    result = ''
    for line in lines:
        if line.strip().startswith('#') or len(line.strip().split()) > 1:
            result += line + '\n'
        else:
            result += '\n'
    return result

def remove_newlines(md_content):
    lines = md_content.split('\n')
    result = ''
    for i in range(len(lines)-1):
        if lines[i] and lines[i+1]:
            result += lines[i] + ' '
        else:
            result += lines[i] + '\n'
    result += lines[-1]
    return result

def remove_header(md_content):
    # find the first line with the least amount of #s
    lines = md_content.split('\n')
    min_count = 7
    min_index = -1
    for i in range(len(lines)):
        if lines[i].startswith('#') and lines[i].count('#') < min_count:
            min_count = lines[i].count('#')
            min_index = i
    if min_index != -1:
        return '\n'.join(lines[min_index:])
    return md_content

def remove_footer(md_content):
    # find the last line with the most amount of #s
    lines = md_content.split('\n')
    max_count = 0
    max_index = -1
    for i in range(len(lines)):
        if lines[i].startswith('#') and lines[i].count('#') >= max_count:
            max_count = lines[i].count('#')
            max_index = i
    if max_index != -1:
        lines = lines[:max_index]
        index = len(lines) - 1
        for i in range(len(lines)-1, -1, -1):
            if lines[i].strip().startswith('#') or lines[i].strip() == '':
                index = i
            else:
                break
        if len(''.join(lines[index:]).strip()) < 100:
            return md_content
        return '\n'.join(lines[:index])
    return md_content

def edit_urls(md_content, url):
    return md_content.replace("](/", "](" + url + "/")
    # wherever we encounter ](/, replace with ](url/
    
def replace_newlines(text):
    return re.sub("\n{3,}", "\n\n", text)
def get_summary(chunks):
    text = ''
    token_count = 0
    for chunk in chunks:
        if token_count + get_token_count(chunk['text']) > 5000:
            continue
        text += chunk['text'] + '\n'
        token_count += get_token_count(chunk['text'])
    system_message = "Your only job is to summarize any input provided to you."
    return handle_chat(messages=[{'role': 'system', 'content': system_message}, {'role': 'user', 'content': text + '\n Summarize the above text:'}], model=model, max_tokens=200)

def get_summaries(results):
    if len(results) == 0:
        return
    if 'summary' in results[0]:
        return

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_summary, result['chunks']) for result in results]
        for future in futures:
            i = futures.index(future)
            results[i]['summary'] = future.result()
        executor.shutdown(wait=True)
    st.session_state['object']['results'] = results

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
    #keywords = turbo_boogle(messages=messages, model=model)
    return keywords # u here? it just gave a perfect response

def respond(results, index):
    website = results[index]
    keywords = generate_keywords(website)
    keywords_embedding = embedding_function(keywords)
    website['chunks'].sort(key=lambda x: cosine_similarity(x['embedding'], keywords_embedding), reverse=True)
    relevant_text = []
    token_count = 0
    for i in range(len(website['chunks'])):
        if token_count + get_token_count(website['chunks'][i]['text']) > 5000:
            continue
        relevant_text.append(website['chunks'][i]['text'])
        token_count += get_token_count(website['chunks'][i]['text'])
    relevant_text_str = '\n'.join(relevant_text)
    print(token_count, 'tokens')
    system_message = generate_chat_system_message(relevant_text_str, website['url'], website['title'])

    messages = []
    token_count = get_token_count(system_message)
    print('-----------------------------------')
    for i in range (len(website['chat'])-1, -1, -1):
        if i == len(website['chat']) - 1 or i == len(website['chat']) - 2:
            token_count += get_token_count(website['chat'][i]['content'])
        else:
            token_count += get_token_count(website['chat'][i]['summary'])
        if token_count > 7000:
            break
        if i == len(website['chat']) - 1 or i == len(website['chat']) - 2:
            message = {'role': website['chat'][i]['role'], 'content': website['chat'][i]['content']}
        else:
            message = {'role': website['chat'][i]['role'], 'content': website['chat'][i]['summary']}
        messages.insert(0, message)
    insert_index = len(messages) - 3
    if insert_index < 0:
        insert_index = 0
    messages.insert(insert_index, {'role': 'system', 'content': system_message})
    print("messages")
    print(messages)
    response = turbo_boogle(messages=messages, model=model, max_tokens=1000)
    #response = turbo_boogle(messages=messages, model=model, max_tokens=1000)
    print("response")
    print(response)
    system_message = "Your only job is to summarize any input provided to you."
    messages = [{'role': 'system', 'content': system_message},
                {'role': 'user', 'content': response + '\n Summarize the above text:'}]
    summary = handle_chat(messages=messages, model=model, max_tokens=200)
    #summary = turbo_boogle(messages=messages, model=model, max_tokens=200)
    message = {'role': 'assistant', 'content': response, 'summary': summary}
    return message


def get_image_icon(base64_string):
    try:
        if base64_string:
            # Get the image data without the "data:image/png;base64," part
            base64_data = base64_string.split(',', 1)[1]
            # Decode the Base64 string, convert that decoded data to bytes
            plain_data = base64.b64decode(base64_data)
            bytes_buffer = BytesIO(plain_data)

            # Open an image from the bytes buffer
            img = Image.open(bytes_buffer)
            return img
    except Exception as e:
        print(f"Error occurred while decoding base64 string : {str(e)}")
    return None

def split_content(website, length=800):
    content_tokens = enc.encode(website['content'].replace('<|endoftext|>', ''))
    if len(content_tokens) > length:
        reminder = len(content_tokens) % length
        division_result = len(content_tokens) // length
        length = length + reminder // division_result + 1
    content_chunks = [content_tokens[i:i+length] for i in range(0, len(content_tokens), length)]
    content_text_chunks = [{"text": enc.decode(chunk), "order": i} for i, chunk in enumerate(content_chunks)]
    website['chunks'] = content_text_chunks
    return website

def get_embeddings(website):
    time_start = time.time()
    if all('embedding' in chunk for chunk in website['chunks']):
        print('All chunks already have embeddings', time.time() - time_start)
        return website
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(embedding_function, chunk['text']) for chunk in website['chunks']]
        for future in futures:
            i = futures.index(future)
            website['chunks'][i]['embedding'] = future.result()
        executor.shutdown(wait=True)
        print('All chunks now have embeddings', time.time() - time_start)
    return website

def process_website(json_object, index):
    if json_object[index]['processed']:
        return json_object
    print('Processing website')
    print('Initial content length:', len(json_object[index]['content']))
    json_object[index]['content'] = remove_newlines(json_object[index]['content'])
    print('Content length after removing newlines:', len(json_object[index]['content']))
    json_object[index]['content'] = remove_lines_inbetween(json_object[index]['content'])
    print('Content length after removing lines inbetween:', len(json_object[index]['content']))
    json_object[index]['content'] = remove_nested_newlines(json_object[index]['content'])
    print('Content length after removing nested newlines:', len(json_object[index]['content']))
    json_object[index]['content'] = remove_header(json_object[index]['content'])
    print('Content length after removing header:', len(json_object[index]['content']))
    json_object[index]['content'] = remove_footer(json_object[index]['content'])
    print('Content length after removing footer:', len(json_object[index]['content']))
    json_object[index]['content'] = edit_urls(json_object[index]['content'], json_object[index]['url'])
    print('Content length after editing urls:', len(json_object[index]['content']))
    json_object[index]['content'] = remove_trash(json_object[index]['content'])
    print('Content length after removing trash:', len(json_object[index]['content']))
    json_object[index]['content'] = replace_newlines(json_object[index]['content'])
    print('Content length after replacing newlines:', len(json_object[index]['content']))
    json_object[index] = split_content(json_object[index])
    json_object[index] = get_embeddings(json_object[index])
    #with open(f'speed_test/{json_object[index]["title"]}_new.md', 'w') as f:
    #    f.write(json_object[index]['content'])
    #f.close()
    json_object[index]['processed'] = True
    return json_object

#st.title('Readability')
if st.session_state['selected_website'] is None:
    col_spacer1, col_content, col_spacer2 = st.columns([1,7,1])
    container = col_content.container()
    col1, col2, col3,col4 = st.columns([1,1,3,4])
 
   # with st.form(key='search_form', clear_on_submit=True):
    with container: 

      #  text_col, submit_col, enhance_col = st.columns([6,1])

        user_input = st.text_area("🔍 Search",placeholder="Search Readability or enter a URL", label_visibility='hidden',key='user_input', height=15, value=st.session_state['query'])
   
       # st.title('')
       # st.markdown('')
        #if user_input:
          #  enhance_col.markdown('')
          #  enhance_col.title('')
        submit_button = col2.button(label='🔍 Search')
        if user_input:
            boost_search = col3.button(label='🚀 Boost Search',key='enhance_button',)
            

            if boost_search:
                boosted_query = ''
                if(st.session_state["selected_time"] !='default'):
                    user_input = f'after:{st.session_state["selected_time"]} ' + user_input
                if(st.session_state['search_websites'] is not None):
                    for i, website in enumerate(st.session_state['search_websites']):
                        if i == 0:
                            user_input = f'site:{website_pairs[website]} ' + user_input
                            if(len(st.session_state['search_websites']) > 1):
                                user_input = '(' + user_input
                        if i == 1:
                            user_input =  f'site:{website_pairs[website]} ' + 'OR' ' ' + user_input
                        
                        if i > 1:
                            if(i == len(st.session_state['search_websites']) - 1):
                                user_input =  f'site:{website_pairs[website]} ' + ' OR ' ' ' + user_input + ')'
                            else:
                                user_input =  f'site:{website_pairs[website]} ' + ' OR ' ' ' + user_input
                boosted_query = get_boosted_query(user_input)
                
               # print(boosted_query)
                update_query(boosted_query)
                
                st.experimental_rerun()



                #st.session_state['user_input_box'] = st.empty()

    if user_input and submit_button:
            st.session_state['query'] = user_input
            st.session_state['quick_response'] = ''
            st.session_state['object'] = None
            st.session_state['timestamp'] = None
            timestamp = time.time()
            st.session_state['timestamp'] = timestamp

            if(st.session_state['selected_time'] != 'default'):
                user_input = f'after:{st.session_state["selected_time"]} ' + user_input
            if(st.session_state['search_websites'] is not None):
                for i, website in enumerate(st.session_state['search_websites']):
                    if i == 0:
                        user_input = f'site:{website_pairs[website]} ' + user_input
                        if(len(st.session_state['search_websites']) > 1):
                            user_input = '(' + user_input
                    if i == 1:
                        user_input =  f'site:{website_pairs[website]} ' + 'OR' ' ' + user_input
                        
                    if i > 1:
                        if(i == len(st.session_state['search_websites']) - 1):
                            user_input =  f'site:{website_pairs[website]} ' + ' OR ' ' ' + user_input + ')'
                        else:
                            user_input =  f'site:{website_pairs[website]} ' + ' OR ' ' ' + user_input

                    

              #  user_input = f'site:{st.session_state["search_websites"]} ' + user_input
            print(user_input)
            st.session_state['object'] = json.load(open(search(user_input, timestamp), "r"))
            os.remove(search(user_input, timestamp))
            if len(st.session_state['object']['results']) == 1:
                start_time = time.time()
                st.session_state['object']['results'] = process_website(st.session_state['object']['results'], 0)
                print('Time to process website:', time.time() - start_time)
                st.session_state['selected_website'] = 0
                st.experimental_rerun()
            elif len(st.session_state['object']['results']) > 1:
                st.experimental_rerun()
            else:
                st.session_state['results_error'] = 'No results found. Please try again.'
                st.experimental_rerun()
                
if st.session_state['results_error'] and st.session_state['selected_website'] is None:
    st.write(st.session_state['results_error'])
    st.session_state['results_error'] = None

if st.session_state['object'] and st.session_state['selected_website'] is None:
   
    col_spacer1, col_content2, col_spacer2 = st.columns([1,7,1])    
    
    snippets_str = ''
    for website in st.session_state['object']['results']:
        if website['snippet']:
            snippets_str += website['snippet'] + '\n'
    
    if st.session_state['quick_response']:
        col_content2.markdown("#### Quick Response")
        col_content2.markdown(st.session_state['quick_response'])
    else:
        if not snippets_str:
            snippets_str = 'No snippets found.'
        update_quick_response(user_input, snippets_str)
        col_content2.markdown("#### Quick Response")
        col_content2.markdown(st.session_state['quick_response'])
    
    # botton which says Summarize
    if 'summary' not in st.session_state['object']['results'][0]:
        button = col_content2.button("Summarize", key='summarize_button')
        if button:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(process_website, st.session_state['object']['results'], i) for i in range(len(st.session_state['object']['results']))]
                for future in futures:
                    i = futures.index(future)
                    st.session_state['object']['results'][i] = future.result()[i]
                executor.shutdown(wait=True)
            get_summaries(st.session_state['object']['results'])
            st.experimental_rerun()

    for i, website in enumerate(st.session_state['object']['results']):
        base64_string = website['favicon'].strip()
        icon = None
        if base64_string.startswith("data:image/"):
            icon = get_image_icon(base64_string)
            icon = pil_to_b64(icon)
        with st.container():
            if i == 0:
                str_view = 'Found ' + '**' + str(len(st.session_state['object']['results'])) + '**' + ' results'

               # if(st.session_state['time_selection']!='default' and st.session_state['time_selection'] is not None):
                #    str_view += '* after ' + '**' + str(st.session_state['time_selection']).replace('-','/') + '**'
                st.markdown(str_view)
            #else:
              #  st.markdown("---")
            cola,colb, = st.columns([1,7])
            if icon:
                with cola:
                    st.markdown(
    f"""<div style="position: relative; border-radius:50%; background-color: #fafafa; width: 25px; height: 25px;">
            <img src="data:image/png;base64,{icon}" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 70%; height: 70%;" />
        </div>""", 
    unsafe_allow_html=True)

            # Title and snippet
            with colb:
                st.markdown(f"**[{website['title'].strip()}]({website['url'].strip()})**", unsafe_allow_html=True)
                st.write(website['snippet'].strip()) # changed from st.text to st.write
                if 'summary' in website and website['summary'].strip():
                    st.markdown(f"**Summary:** {website['summary']}")

            # Button
            with colb:
                if st.button("Chat", key=f"website_{i}"):
                    print(i)
                    start_time = time.time()
                    st.session_state['object']['results'] = process_website(st.session_state['object']['results'] , i)
                    print('Time to process website:', time.time() - start_time)
                    print(i)
                    st.session_state['selected_website'] = i
                    st.experimental_rerun()


if st.session_state['selected_website'] is not None:

    col1, col2 = st.columns([1, 1])
    container = col1.container()
    markdown_chat_data = "#### Chat"
    with container:
        back_button = st.button("Back", key='back_button')
        if back_button:
            st.session_state['selected_website'] = None
            st.experimental_rerun()
        for message in st.session_state['object']['results'][st.session_state['selected_website']]['chat']:
            markdown_chat_data += '\n####' + message['role'] + '\n' + message['content']
        html_chat_data = markdown(markdown_chat_data)
        # Custom CSS for the HTML content
        custom_css = """
        <style>
            img {
                max-width: 100%;
                height: auto;
            }
            body {
                font-family: "Helvetica Neue", Arial, sans-serif;
                font-size: 14px;
                line-height: 1.42857143;
                color: #333;
            }
        </style>
        """
        html_chat_data += '<script type="text/javascript">window.scrollTo(0,document.body.scrollHeight);</script>'
        # Include CSS styling in the HTML content
        html_chat_data = custom_css + html_chat_data

        # Specify height and enable scrolling
        components.html(html_chat_data, height=600, scrolling=True)

            #st.write("#### " + message['role'] + "\n" + message['content'])
        with st.form(key='message_form', clear_on_submit=True):
            
            user_message = st.text_area("Ask about the website", key='user_message', height=100)
            col3, col4, col5 = st.columns([1, 1, 1])
            submit_button = col3.form_submit_button(label='Send')
            #back_button = col5.form_submit_button(label='Back')


        if submit_button and user_message:
            system_message = "Your only job is to summarize any input provided to you."
            messages = [{'role': 'system', 'content': system_message},
                       {'role': 'user', 'content': user_message + '\n Summarize the above text:'}]
            summary = user_message
            if get_token_count(user_message) > 200:
                summary = handle_chat(messages=messages, model=model, max_tokens=200)
                #summary = turbo_boogle(messages=messages, model=model, max_tokens=200)
            st.session_state['object']['results'][st.session_state['selected_website']]['chat'].append({'role': 'user', 'content': user_message, 'summary': summary})
            try:
                st.session_state['object']['results'][st.session_state['selected_website']]['chat'].append(respond(st.session_state['object']['results'], st.session_state['selected_website']))
            except Exception as e:
                print(e)
                st.session_state['object']['results'][st.session_state['selected_website']]['chat'].append({'role': 'assistant', 'content': 'I am sorry, there was an error. Please try again.', 'summary': 'I am sorry, I do not understand. Please try again.'})
            st.experimental_rerun()
        #if back_button:
        #    st.session_state['selected_website'] = None
        #    st.experimental_rerun()

    
    with col2:
        button_text = "Reader View" if not st.session_state['reader_view'] else "Website View"
        reader_button = st.button(button_text, key='reader_button')
        if reader_button:
            st.session_state['reader_view'] = not st.session_state['reader_view']
            st.experimental_rerun()
        if st.session_state['reader_view']:
            markdown_data = st.session_state['object']['results'][st.session_state['selected_website']]['content']
            html_data = markdown(markdown_data)
            # Custom CSS for the HTML content
            custom_css = """
            <style>
                img {
                    max-width: 100%;
                    height: auto;
                }
                body {
                    font-family: "Helvetica Neue", Arial, sans-serif;
                    font-size: 14px;
                    line-height: 1.42857143;
                    color: #333;
                }
          
            </style>
            """
            # Include CSS styling in the HTML content
            html_data = custom_css + html_data
            # Specify height and enable scrolling
            components.html(html_data, height=800, scrolling=True)
        else:
            # toggle 1:
            html_data = st.session_state['object']['results'][st.session_state['selected_website']]['data']
            html_data = f"<div style='pointer-events: none;'>{html_data}</div>"
            #st.header("Show an external HTML")
            st.components.v1.html(html_data, height=800, scrolling=True)
            #st.components.v1.iframe(st.session_state['object']['results'][st.session_state['selected_website']]['url'], scrolling=True, height=800)


with st.sidebar:
    st.markdown("<h1 style='margin-bottom:0'> Tools </h1>",
                unsafe_allow_html=True)  # remove margin bottom
    options = ["Sources", "Time", "Model"]

    option = st.radio("Tools", options,
                      label_visibility="hidden", horizontal=True)
    st.markdown("___")
    if option == "Time":


        time_selection = st.radio(
            "Results from", st.session_state["time_options"],)
        

        if time_selection != "Any Time":
            if time_selection == "Past Hour":
                st.session_state["selected_time"] = datetime.now() - timedelta(hours=1)
                #Move "Past Hour" to the top of the list
                st.session_state["time_options"].remove("Past Hour")
                st.session_state["time_options"].insert(0, "Past Hour")
            elif time_selection == "Past Day":
                st.session_state["selected_time"] = datetime.now() - timedelta(days=1)
                st.session_state["time_options"].remove("Past Day")
                st.session_state["time_options"].insert(0, "Past Day")
            elif time_selection == "Past Week":
                st.session_state["selected_time"] = datetime.now() - timedelta(weeks=1)
                st.session_state["time_options"].remove("Past Week")
                st.session_state["time_options"].insert(0, "Past Week")
            elif time_selection == "Past Month":
                st.session_state["selected_time"] = datetime.now() - timedelta(days=30)
                st.session_state["time_options"].remove("Past Month")
                st.session_state["time_options"].insert(0, "Past Month")
            elif time_selection == "Past Year":
                st.session_state["selected_time"] = datetime.now() - timedelta(days=365)
                st.session_state["time_options"].remove("Past Year")
                st.session_state["time_options"].insert(0, "Past Year")
            st.session_state["selected_time"] = st.session_state["selected_time"].strftime("%Y-%m-%d")
        else: 
            st.session_state["selected_time"] = 'default'

    if option == "Sources":
        for category, websites in websites_by_category.items():

            st.markdown(f"## {category}")

            for website in websites:
                checkbox_key = f"{category}-{website['name']}"
                favicon_url = f"https://www.google.com/s2/favicons?sz=16&domain_url={website['url']}"

                with st.container():
                    col1, col2 = st.columns([10, 1])
                    col2.markdown(f"![Icon]({favicon_url})")
                    
                    if st.session_state['search_websites'] is None:
                        checkbox = col1.checkbox(label=website['name'],value= False, key=checkbox_key)
                    else:
                        checkbox = col1.checkbox(label=website['name'],value= website['name'] in st.session_state['search_websites'], key=checkbox_key)
                    
                    if checkbox:
                        if st.session_state['search_websites'] is None:
                            st.session_state['search_websites'] = []

                        if website['name'] not in st.session_state['search_websites']:
                            st.session_state['search_websites'].append(website['name'])
                    else:
                        if st.session_state['search_websites'] is None:
                            st.session_state['search_websites'] = []
                        if website['name'] in st.session_state['search_websites']:
                            st.session_state['search_websites'].remove(website['name'])


    if option == "Model":
        st.session_state['model'] = st.selectbox("Model", ['Chat', 'Code',])
        st.session_state['model_settings']['temperature'] = st.slider("Creativity", 0.0, 1.0, 0.2)
    #    st.session_state['model_settings']['token_count'] = st.slider("Word Limit", 50, 750, 300)
   #     st.session_state['model_settings']['top_p'] = st.slider("Diversity", 0.0, 1.0, 0.8)
    #    st.session_state['model_settings']['top_k'] = st.slider("Predictability", 1, 40, 40)


st.markdown("""
  <style>
    .css-o18uir.e16nr0p33 {
      margin-top: -100px;
    }
  </style>
""", unsafe_allow_html=True)

hi = """## If khan academy prefix is site:khanacademy.org ## If abc.com and cdb.com prexif is (site:abc.com OR site:cdb.com)"""
