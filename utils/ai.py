import openai
import numpy as np
import tiktoken
import os
enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
# Use environment variable to set API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def turbo_boogle(messages=[], max_tokens=1000, temperature=0.7, model="gpt-4", stream=False):
    response = openai.ChatCompletion.create(
        model=model, messages=messages, max_tokens=max_tokens, temperature=temperature, stream=stream)
    if stream:
        return response
    response_str = ""
    for i in range(len(response['choices'])):
        response_str += response['choices'][i]['message']['content']
    return response_str

def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    if text == "":
        text = "None"
    try:
        return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']
    except Exception as e:
        print(f'Error getting embedding for {text}: {e}')
        return None

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_default_embedding():
    # check if default embedding exists
    default_embedding = np.load('utils/default_embedding.npy')
    return default_embedding

def get_token_count(text):
    return len(enc.encode(text))

def embedding_function(text, num_retries=0):
    print(num_retries)
    embedding = None
    if text == '':
        return get_default_embedding()
    try: 
        embedding = get_embedding(text)
    except Exception as e:
        print(f'Error in embedding_function')
        embedding = None
    if embedding is None:
        if num_retries < 3:
            embedding = embedding_function(text, num_retries + 1)
        else:
            print(f'Error in embedding_function: embedding is None. Returning default embedding.')
            embedding = get_default_embedding()
    return embedding

if __name__ == "__main__":
    text = """Hello, I am a human.
    I am a human.
    """
    embedding = embedding_function(text)