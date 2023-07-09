from researcher2 import search
import json
import streamlit as st
from utils.ai import cosine_similarity, turbo_boogle, embedding_function, get_token_count
from utils.prompts import generate_chat_system_message, generate_keyword_prompt
from vertex_test import handle_chat
model = "gpt-3.5-turbo-16k"


def generate_keywords(website):
    token_count = 0
    messages = []
    system_message = generate_keyword_prompt(website['url'], website['title'])
   # messages.append({'author': 'system', 'content': system_message})
    for i in range (len(website['chat'])-1, -1, -1):
        token_count += get_token_count(website['chat'][i]['content'])
        if token_count > 2000:
            break
        message = {'author': website['chat'][i]['author'], 'content': website['chat'][i]['content']}
        messages.insert(0, message)
    # WE DO NEED THE MESSAGE (MODIFIED) BELOW BECAUSE IT ACTUALLY GENERATES A RESPONSE INSTEAD OF THE KEYWORDS
    #messages.append({'author': 'user', 'content': 'List of keywords:'})
    keywords = handle_chat(human_msg = 'List of keywords:', messages=messages, context=system_message)
    return keywords # u here? it just gave a perfect response

def respond(json_object, index):
    website = json_object[index]
    keywords = generate_keywords(website)
    keywords_embedding = embedding_function(keywords)
    website['content'].sort(key=lambda x: cosine_similarity(x['embedding'], keywords_embedding), reverse=True)
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
    token_count = get_token_count(system_message)
    print('-----------------------------------')
    for i in range (len(website['chat'])-1, -1, -1):
        if i == len(website['chat']) - 1 or i == len(website['chat']) - 2:
            token_count += get_token_count(website['chat'][i]['content'])
        else:
            token_count += get_token_count(website['chat'][i]['summary'])
        if token_count > 8000:
            break
        if i == len(website['chat']) - 1 or i == len(website['chat']) - 2:
            message = {'author': website['chat'][i]['author'], 'content': website['chat'][i]['content']}
        else:
            message = {'author': website['chat'][i]['author'], 'content': website['chat'][i]['summary']}
        messages.insert(0, message)
   # messages.insert(0, {'author': 'system', 'content': system_message})
    print("messages")
    print(messages)
    human_msg = messages[-1]['content']
    messages = messages[:-1]
    response = handle_chat(human_msg=human_msg, context=system_message, messages=messages, )
    print("response")
    print(response)
    system_message = "Your only job is to summarize any input provided to you."
  #  messages = [
               # {'author': 'user', 'content': response + '\n Summarize the above text:'}]
    summary = handle_chat(human_msg = "Summarize the text above. Summary:\n",context=system_message, messages=messages, )
    message = {'author': 'assistant', 'content': response, 'summary': summary}
    return message





if 'object' not in st.session_state:
    st.session_state['object'] = None
if 'selected_website' not in st.session_state:
    st.session_state['selected_website'] = None


if st.session_state['selected_website'] is None:
    container = st.container()
    with container:
        with st.form(key='search_form', clear_on_submit=True):
            user_input = st.text_area("Search for anything", key='user_input', height=100)
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            st.session_state['object'] = None
            print(search(user_input))
            st.session_state['object'] = json.load(open(search(user_input)))

if st.session_state['object'] and st.session_state['selected_website'] is None:
    for i, website in enumerate(st.session_state.object):
        if st.button(f"{i+1}. #### {website['title'].strip()}\n{website['snippet'].strip()[:200]}", key=f"website_{i}"):
            st.session_state['selected_website'] = i
            if st.session_state.object[st.session_state.selected_website]['chat'][-1]['author'] != 'assistant':
                st.session_state.object[st.session_state.selected_website]['chat'].append(respond(st.session_state.object, st.session_state.selected_website))
            st.experimental_rerun()

if st.session_state['selected_website'] is not None:
    # make a back button
    container = st.container()
    with container:
        with st.form(key='back_form', clear_on_submit=True):
            back_button = st.form_submit_button(label='Back')
            if back_button:
                st.session_state['selected_website'] = None
                st.experimental_rerun()

if st.session_state['selected_website'] is not None:
    for message in st.session_state.object[st.session_state.selected_website]['chat']:
        st.write("#### " + message['author'] + "\n" + message['content'])
    
    container = st.container()
    with container:
        with st.form(key='message_form', clear_on_submit=True):
            user_message = st.text_area("Type your message here", key='user_message', height=100)
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_message:
            system_message = "Your only job is to summarize any input provided to you."
        #   messages = [#{'author': 'system', 'content': system_message},
                     #  {'author': 'user', 'content': user_message + '\n Summarize the above text:'}]
            summary = user_message
            if get_token_count(user_message) > 200:
                summary = handle_chat( human_msg =  user_message + "\n Summarize the above text: ",messages=[], context=system_message)
            st.session_state.object[st.session_state.selected_website]['chat'].append({'author': 'user', 'content': user_message, 'summary': summary})
            st.session_state.object[st.session_state.selected_website]['chat'].append(respond(st.session_state.object, st.session_state.selected_website))
            # reset the container
            st.experimental_rerun()
    
#if st.session_state['selected_website'] is not None:
    #st.write("#### Assistant\n" + st.session_state.object[st.session_state.selected_website]['chat'][-1]['content'])


#there needs to be stateful variable which handles all of the urls
#it will gegt updated whevner the user clicks on a submit button

#the content of it will b e shown whenever there is not a website selected

#therefore there will alos have to be a variable which tracks the current website

#the current website will be updated whenever the user clicks on a url button from the list of urls

#whenever a current website is selected there will be a back button


#The back button when pressed will trigger the websites conversation to be saved and the current website to be set to none

#the back button will also trigger the list of urls to be shown again

#there will be another variable which tracks which websites have been visited along with the messages they exchanged

#the page with urls will have a text button with submission to generate a new list of urls