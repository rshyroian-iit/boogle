from search import search
import json
from io import BytesIO
from PIL import Image
import streamlit as st
import base64
from utils.ai import cosine_similarity, turbo_boogle, embedding_function, get_token_count
from utils.prompts import generate_chat_system_message, generate_keyword_prompt
import time
import concurrent.futures
from markdown import markdown
from datetime import datetime, timedelta
import tiktoken
enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
selected_time = 'default'
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
# Load the websites_by_category dictionary from the JSON file
with open('websites_by_category.json', 'r') as f:
    websites_by_category = json.load(f)

# Create a dictionary to store the state of each checkbox
checkbox_states = {}


if 'object' not in st.session_state:
    st.session_state['object'] = None
if 'selected_website' not in st.session_state:
    st.session_state['selected_website'] = None
if 'timestamp' not in st.session_state:
    st.session_state['timestamp'] = None
    #Your muted on Discord
if 'results_error' not in st.session_state:
    st.session_state['results_error'] = None
if 'model_settings' not in st.session_state:
    st.session_state['model_settings'] = None


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
    # find the matching opening square bracket
    for j in range(1, i+1):
        if md_content[i-j] == ']':
            closing_square_bracket_count += 1
        elif md_content[i-j] == '[':
            closing_square_bracket_count -= 1
            if closing_square_bracket_count == 0:
                opening_square_bracket_index = i-j
                break
    # find the matching closing parentheses
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
        #print(i)
        if md_content[i] == ']' and md_content[i+1] == '(':
            j, k = find_matching_parentheses(md_content, i)
            #print(j, k)
            if j != -1 and k != -1:
                brackets_content = md_content[j+1:i]
                parentheses_content = md_content[i+2:k]
                if '\n' in brackets_content or '\n' in parentheses_content:
                    md_content = md_content[:j+1] + brackets_content.replace('\n', ' ') + md_content[i: i+2] + parentheses_content.replace('\n', ' ').replace(' ', '') + md_content[k:]
                    #print(len(brackets_content), len(parentheses_content))
                    i = j + len(brackets_content.replace('\n', ' ')) + 2 + len(parentheses_content.replace('\n', ' ').replace(' ', '')) + 1
        i += 1
    return md_content

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
        md_content = '\n'.join(lines[:max_index])
        lines = md_content.split('\n')
        index = len(lines) - 1
        for i in range(len(lines)-1, -1, -1):
            if lines[i].strip().startswith('#') or lines[i].strip() == '':
                index = i
            else:
                break
        return '\n'.join(lines[:index])
    return md_content

def edit_urls(md_content, url):
    return md_content.replace("](/", "](" + url + "/")
    # wherever we encounter ](/, replace with ](url/

    

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

def respond(json_object, index):
    website = json_object[index]
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
    print("response")
    print(response)
    system_message = "Your only job is to summarize any input provided to you."
    messages = [{'role': 'system', 'content': system_message},
                {'role': 'user', 'content': response + '\n Summarize the above text:'}]
    summary = turbo_boogle(messages=messages, model=model, max_tokens=200)
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
    json_object[index]['content'] = remove_newlines(json_object[index]['content'])
    json_object[index]['content'] = remove_nested_newlines(json_object[index]['content'])
    json_object[index]['content'] = remove_header(json_object[index]['content'])
    json_object[index]['content'] = remove_footer(json_object[index]['content'])
    json_object[index]['content'] = edit_urls(json_object[index]['content'], json_object[index]['url'])
    #json_object[index]['content'] = remove_trash(json_object[index]['content'])
    json_object[index] = split_content(json_object[index])
    json_object[index] = get_embeddings(json_object[index])
    return json_object

#st.title('Readability')
if st.session_state['selected_website'] is None:
    col_spacer1, col_content, col_spacer2 = st.columns([1,6,1])
    container = col_content.container()
   
 
   # with st.form(key='search_form', clear_on_submit=True):
    with container: 

        text_col, submit_col = st.columns([6,1])

        user_input = text_col.text_area("🔍",placeholder="Search for anything", label_visibility='hidden',key='user_input', height=15)
        submit_col.title('')
        submit_col.markdown('')
        submit_button = submit_col.button(label='🔍')


    if  user_input and submit_button:
            st.session_state['object'] = None
            st.session_state['timestamp'] = None
            timestamp = time.time()
            st.session_state['timestamp'] = timestamp
            if(selected_time !='default'):
                user_input = f'after:{selected_time} ' + user_input

            st.session_state['object'] = json.load(open(search(user_input, timestamp), "r"))
            if len(st.session_state['object']) == 1:
                start_time = time.time()
                st.session_state['object'] = process_website(st.session_state['object'], 0)
                print('Time to process website:', time.time() - start_time)
                st.session_state['selected_website'] = 0
                st.experimental_rerun()
            elif len(st.session_state['object']) > 1:
                st.experimental_rerun()
            else:
                st.session_state['results_error'] = 'No results found. Please try again.'
                st.experimental_rerun()
                
if st.session_state['results_error'] and st.session_state['selected_website'] is None:
    st.write(st.session_state['results_error'])
    st.session_state['results_error'] = None

if st.session_state['object'] and st.session_state['selected_website'] is None:
    with text_col.expander('What I Searched', expanded=False):
        st.write('hello1')
        st.write('hello2')
        st.write('hello3')
    text_col.markdown("#### Quick Response")
    text_col.markdown("The answer to the quick response goes here. The answer to the quick response goes here. The answer to the quick response goes here. The answer to the quick response goes here.")


    for i, website in enumerate(st.session_state.object):
        base64_string = website['favicon'].strip()
        icon = None
        if base64_string.startswith("data:image/"):
            icon = get_image_icon(base64_string)
            icon = pil_to_b64(icon)

        with st.container():
            st.markdown("---")
            cola,colb, = st.columns([1,7])

            # Icon with white circular background
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

            # Button
            with colb:
                if st.button("Use AI", key=f"website_{i}"):
                    print(i)
                    start_time = time.time()
                    st.session_state['object'] = process_website(st.session_state['object'], i)
                    print('Time to process website:', time.time() - start_time)
                    print(i)
                    st.session_state['selected_website'] = i
                    st.experimental_rerun()


if st.session_state['selected_website'] is not None:

    col1, col2 = st.columns([1, 1])
    container = col1.container()

    with container:
        for message in st.session_state.object[st.session_state.selected_website]['chat']:
            st.write("#### " + message['role'] + "\n" + message['content'])
        with st.form(key='message_form', clear_on_submit=True):
            
            user_message = st.text_area("Type your message here", key='user_message', height=100)
            submit_button = st.form_submit_button(label='Send')


        if submit_button and user_message:
            system_message = "Your only job is to summarize any input provided to you."
            messages = [{'role': 'system', 'content': system_message},
                       {'role': 'user', 'content': user_message + '\n Summarize the above text:'}]
            summary = user_message
            if get_token_count(user_message) > 200:
                summary = turbo_boogle(messages=messages, model=model, max_tokens=200)
            st.session_state.object[st.session_state.selected_website]['chat'].append({'role': 'user', 'content': user_message, 'summary': summary})
            try:
                st.session_state.object[st.session_state.selected_website]['chat'].append(respond(st.session_state.object, st.session_state.selected_website))
            except Exception as e:
                print(e)
                st.session_state.object[st.session_state.selected_website]['chat'].append({'role': 'assistant', 'content': 'I am sorry, there was an error. Please try again.', 'summary': 'I am sorry, I do not understand. Please try again.'})
            st.experimental_rerun()
    
    with col2:
        if st.session_state['object'][st.session_state['selected_website']]['url'].endswith('.pdf'):
            pdf_content_bytes = st.session_state['object'][st.session_state['selected_website']]['data'].encode('utf-8')
            st.write(pdf_content_bytes)
            st.write(type(pdf_content_bytes))
        else:
            if st.checkbox('Show Readibility', False):
                # toggle 2:
                markdown_data = st.session_state['object'][st.session_state['selected_website']]['content']
                html_data = markdown(markdown_data)
                #st.header("Show an external HTML")
                custom_css = """
                <style>
                    img {
                        max-width: 100%;
                        height: auto;
                    }
                </style>
                """
                #st.markdown(custom_css, unsafe_allow_html=True)
                #st.markdown(markdown_data)
                st.components.v1.html(html_data, scrolling=True, height=700)
            else:
                # toggle 1:
                html_data = st.session_state['object'][st.session_state['selected_website']]['data']
                html_data = f"<div style='pointer-events: none;'>{html_data}</div>"
                #st.header("Show an external HTML")
                #st.components.v1.html(html_data, scrolling=True)
                st.components.v1.iframe(st.session_state['object'][st.session_state['selected_website']]['url'], scrolling=True, height=700)

if st.session_state['selected_website'] is not None:
    if col1.button('Back'):
        st.session_state['selected_website'] = None
        st.experimental_rerun()
with st.sidebar:
    st.markdown("<h1 style='margin-bottom:0'> Tools </h1>",
                unsafe_allow_html=True)  # remove margin bottom
    options = ["Date", "Sources", "Model"]

    option = st.radio("Tools", options,
                      label_visibility="hidden", horizontal=True)
    st.markdown("___")
    if option == "Date":
        time_options = ["Any Time", "Past Hour", "Past Day",
                        "Past Week", "Past Month", "Past Year"]
        time_selection = st.radio(
            "Results from", time_options,)
        

        if time_selection != "Any Time":
            if time_selection == "Past Hour":
                selected_time = datetime.now() - timedelta(hours=1)
            elif time_selection == "Past Day":
                selected_time = datetime.now() - timedelta(days=1)
            elif time_selection == "Past Week":
                selected_time = datetime.now() - timedelta(weeks=1)
            elif time_selection == "Past Month":
                selected_time = datetime.now() - timedelta(days=30)
            elif time_selection == "Past Year":
                selected_time = datetime.now() - timedelta(days=365)
            selected_time = selected_time.strftime("%Y-%m-%d")
        else: 
            selected_time = 'default'

    if option == "Sources":
        for category, websites in websites_by_category.items():

            st.markdown(f"## {category}")
           # st.checkbox("Select All", key=f"{category}-select-all")
            for website in websites:
                checkbox_key = f"{category}-{website['name']}"
                favicon_url = f"https://www.google.com/s2/favicons?sz=16&domain_url={website['url']}"
                with st.container():
                    col1, col2 = st.columns([10, 1])
                    col2.markdown(f"![Icon]({favicon_url})")
                    checkbox = col1.checkbox(website['name'], key=checkbox_key)
                    checkbox_states[checkbox_key] = checkbox

    if option == "Model":
        randomness = st.slider("Randomness", 0.0, 1.0, 0.2)
        word_count = st.slider("Word Limit", 50, 750, 300)
    st.write("\n\n\n\n\n\n\n\n\n\n\n")
selected_websites = [key.split('-')[1]
                     for key, checked in checkbox_states.items() if checked]

st.markdown("""
  <style>
    .css-o18uir.e16nr0p33 {
      margin-top: -100px;
    }
  </style>
""", unsafe_allow_html=True)
