import google.cloud.aiplatform as aiplatform
from vertexai.preview.language_models import ChatModel, InputOutputTextPair, ChatMessage, TextGenerationModel
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import vertexai
import json  # add this line
from google.oauth2 import service_account
import numpy as np
import os

# Load the service account json file
# Update the values in the json file with your own
#with open(
#    "service_account.json"
#) as f:  # replace 'serviceAccount.json' with the path to your file if necessary
#    service_account_info = json.load(f)
service_account_info = os.getenv("SERVICE_ACCOUNT_INFO")

my_credentials = service_account.Credentials.from_service_account_info(
    service_account_info
)

# Initialize Google AI Platform with project details and credentials
aiplatform.init(
    credentials=my_credentials,
)

with open("service_account.json", encoding="utf-8") as f:
    project_json = json.load(f)
    project_id = project_json["project_id"]


# Initialize Vertex AI with project and location
vertexai.init(project=project_id, location="us-central1")

print("Initialized Vertex AI")
chat_model = TextGenerationModel.from_pretrained("text-bison")
code_model = TextGenerationModel.from_pretrained("text-bison")

def handle_chat(messages=[], max_tokens=1000, temperature=0.7, model="chat", stream=False):
    input_str = ''
    for message in messages:
        if message['role'] == 'user':
            input_str += 'User: ' + message['content'] + '\n'
        elif message['role'] == 'assistant':
            input_str += 'Assistant: ' + message['content'] + '\n'
        else:
            input_str += 'System: ' + message['content'] + '\n'
    input_str += 'Assistant: '
    
    if model == 'chat':
        response = chat_model.predict(input_str, max_output_tokens=max_tokens, temperature=temperature)
    elif model == 'code':
        response = code_model.predict(input_str, max_output_tokens=max_tokens, temperature=temperature)
    else:
        response = chat_model.predict(input_str, max_output_tokens=max_tokens, temperature=temperature)
    return response.text



#handle_chat('hello', 'Give your answer using Markdown', [{'content': 'hello', 'author': 'user'}])
google_chat_context = "You are an AI Research Assistant tasked with answering a specific research question based on provided website content. Your objective is to provide a well-structured, easily understandable response in markdown format that comprehensively and fairly addresses the research question. Draw only from the information given in the website content and do not make any assumptions or speculations. Your response should be evidence-based, balanced, and it should utilize Markdown to make responses clear and succinct, with emphasis on key points."

def google_chat_examples():
    google_chat_examples = [  InputOutputTextPair(
        input_text="""Website Content: 
        'Artificial Intelligence is changing the healthcare landscape. It enables disease prediction and facilitates personalized patient care. However, concerns over data privacy and the black box nature of AI algorithms are significant.'

        Research Question: "What are the impacts of AI in healthcare?"
        
        Response: """,
        output_text="""# Impacts of AI in Healthcare

        ## Positive Impacts
        - **Disease Prediction and Personalized Care:** AI is transforming healthcare, notably through its capabilities to predict diseases and provide personalized patient care.

        ## Concerns
        - **Data Privacy and AI Opacity:** Significant concerns revolve around data privacy issues and the 'black box' nature of AI algorithms.
        """),
        
    InputOutputTextPair(
        input_text="""Website Content: 
        'Climate change, often linked with increased global temperatures and extreme weather events, continues to be a hotly debated topic. It's also associated with rising sea levels, which can result in devastating floods.'

        Research Question: "What are the major effects of climate change?"
        
        Response: """,
        output_text="""# Major Effects of Climate Change

        ## Increased Temperatures
        - Climate change is often linked with **increased global temperatures**.

        ## Extreme Weather Events
        - It also brings about **extreme weather events**, contributing to the hotly debated nature of the topic.

        ## Rising Sea Levels
        - One significant consequence is **rising sea levels**, which can result in devastating floods.
        """),
        
    InputOutputTextPair(
        input_text="""Website Content: 
        'Cryptocurrency, a digital or virtual currency that uses cryptography for security, is becoming increasingly popular. Bitcoin, the most famous cryptocurrency, has seen significant value growth, but concerns over its volatility and environmental impact persist.'

        Research Question: "What are the key features and concerns of Cryptocurrency?"
        
        Response: """,
        output_text="""# Key Features and Concerns of Cryptocurrency

        ## Features
        - **Digital or Virtual Nature:** Cryptocurrency is a digital or virtual currency.
        - **Security:** It uses cryptography for security.
        - **Popularity:** Cryptocurrencies, especially Bitcoin, are becoming increasingly popular.

        ## Concerns
        - **Volatility:** Bitcoin, the most famous cryptocurrency, is known for its significant value fluctuations.
        - **Environmental Impact:** There are persistent concerns over the environmental impact of cryptocurrency mining.
        """),
    
    InputOutputTextPair(
        input_text="""Website Content: 
        'In the mess of quantum physics, entanglement is a bizarre phenomenon where particles become interconnected. Changes to one particle can instantly affect the other, no matter the distance between them, something Einstein famously dubbed "spooky action at a distance". However, this complex world has the potential to revolutionize computing and communication systems, despite the challenges in practical implementation.'

        Research Question: "What is quantum entanglement and its potential implications?"
        
        Response: """,
        output_text="""# Quantum Entanglement and Its Potential Implications

        ## Quantum Entanglement
        - **Interconnection of Particles:** Quantum entanglement is a bizarre phenomenon where particles become interconnected. Changes to one particle can instantly affect the other, no matter the distance between them, a concept Einstein famously dubbed "spooky action at a distance".

        ## Potential Implications
        - **Revolutionizing Computing and Communication Systems:** Quantum entanglement, despite its complexity and challenges in practical implementation, has the potential to revolutionize computing and communication systems.
        """),

    ]
    return google_chat_examples

def generate_google_keywords_context(url: str, title: str) -> str:
    context = f"You are a language model trained as an expert, scholarly search assistant tasked with extracting crucial keywords from a user's question or statement. These keywords will help in retrieving relevant information from a specified website titled '{title}' and located at URL '{url}'. Your output should be a comma-separated list of keywords precisely and directly related to the user's query. Keep in mind the range of information available on the website when generating keywords. Avoid assumptions and speculative responses, maintain brevity, and ensure your responses are consistent for effective data parsing."
    return context
examples=[
    InputOutputTextPair(
        input_text="""Website Title: "Effects of Climate Change"
        Website URL: "https://www.climatechangeeffects.com"
        User Query: "What are the implications of climate change on polar bear populations?" """,
        output_text="implications, climate change, polar bear, populations"),
        
    InputOutputTextPair(
        input_text="""Website Title: "Digital Marketing Trends"
        Website URL: "https://www.dmtrends.com"
        User Query: "What are the emerging trends in digital marketing in 2023?" """,
        output_text="emerging trends, digital marketing, 2023"),
    
    InputOutputTextPair(
        input_text="""Website Title: "Renewable Energy Sources"
        Website URL: "https://www.renewableenergy.com"
        User Query: "What are the environmental benefits and economic costs of solar power?" """,
        output_text="environmental benefits, economic costs, solar power")
]
