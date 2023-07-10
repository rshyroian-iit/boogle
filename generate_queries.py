import google.cloud.aiplatform as aiplatform
from vertexai.preview.language_models import ChatModel, InputOutputTextPair, ChatMessage
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import vertexai
import json  # add this line
from google.oauth2 import service_account
from ast import literal_eval
import re
# Load the service account json file
# Update the values in the json file with your own
with open(
    "service_account.json"
) as f:  # replace 'serviceAccount.json' with the path to your file if necessary
    service_account_info = json.load(f)

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

chat_model = ChatModel.from_pretrained("chat-bison@001")
parameters = {
    "temperature": 0.5,
    "max_output_tokens": 512,
    "top_p": 0.8,
    "top_k": 40
}
chat = chat_model.start_chat(
    context="""You are an advanced search query generator. Your role is to enhance and refine user search queries to maximize the likelihood of retrieving the most accurate and comprehensive information from Google. The user\'s input could be a simple query, a complex multi-topic question, or even include advanced search operators such as \"site:\", \"before:\", \"after:\", \"intitle:\", etc. If given, these search operators should be incorporated in your refined queries. Your goal is to break down the initial query into a series of refined searches that could range from a single, very specific question to a diverse set of inquiries, depending on the original input complexity. Always present your responses in JSON format.""",
    examples=[
        InputOutputTextPair(
            input_text="""{
  \"userQuery\": \"AI impacts on jobs\"
}""",
            output_text="""{
  \"refinedQueries\": [
    \"AI and job displacement statistics\",
    \"Industries most affected by AI before:2023\",
    \"AI\'s role in job creation after:2021\",
    \"AI impacts on remote work\",
    \"site:https://www.brookings.edu AI and future of jobs\"
  ]
}"""
        ),
        InputOutputTextPair(
            input_text="""{
  \"userQuery\": \"GPT-4 applications in business\"
}
""",
            output_text="""{
  \"refinedQueries\": [
    \"GPT-4 applications in finance sector\",
    \"Case studies of GPT-4 use in small businesses\",
    \"GPT-4 impacts on business productivity\",
    \"site:https://www.hbr.org GPT-4 and business strategies\",
    \"GPT-4 in business automation before:2023\"
  ]
}"""
        ),
      
        InputOutputTextPair(
            input_text="""{
  \"userQuery\": \"COVID-19 vaccines and AI in healthcare\"
}""",
            output_text="""{
  \"refinedQueries\": [
    \"AI\'s role in COVID-19 vaccine development\",
    \"Use of AI in COVID-19 vaccine distribution\",
    \"AI in predicting vaccine effectiveness studies\",
    \"AI applications in telehealth during COVID-19\",
    \"site:https://www.who.int AI and pandemic response\"
  ]
}"""
        ),
        InputOutputTextPair(
            input_text="""{
  \"userQuery\": \"COVID-19 vaccines and AI in healthcare\"
}""",
            output_text="""{
  \"refinedQueries\": [
    \"Latest COVID-19 vaccine developments\",
    \"Role of AI in COVID-19 vaccine distribution\",
    \"Use of AI in predicting vaccine effectiveness\",
    \"AI applications in pandemic response\",
    \"How has AI changed healthcare delivery during COVID-19?\"
  ]
}"""
        ),
        InputOutputTextPair(
            input_text="""{
  \"userQuery\": \"Effects of climate change on agriculture\"
}""",
            output_text="""{
  \"refinedQueries\": [
    \"Climate change impacts on crop yield\",
    \"Climate change and its effects on irrigation\",
    \"site:https://www.nature.com climate change and agriculture research\",
    \"Farmers\' adaptation to climate change\",
    \"Climate change effects on agriculture in developing countries after:2022\"
  ]
}"""
        )
    ]
)

def get_search_queries(prompt, max_queries=5):
    input_json = {}
    input_json['userQuery'] = prompt
    response = chat.send_message(str(input_json))
    
    # We are not going to use literal_eval here. Instead, we'll parse the response manually
    response_text = response.text
    
    # Using regex to find all the substrings that are enclosed within double quotes
    # Each such substring corresponds to a query
    queries = re.findall(r'"([^"]*)"', response_text)
    
    # The first item in the list is the key 'refinedQueries', so we remove it
    queries.pop(0)
    if(len(queries) > max_queries):
        queries = queries[:max_queries]
   # queries = queries[:max_queries]
    
    return queries

#get_search_queries('after:2023 world series winner')

