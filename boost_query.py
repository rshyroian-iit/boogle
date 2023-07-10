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


# Initialize Vertex AI with project and location
vertexai.init(project=project_id, location="us-central1")
context = """You are an advanced search query enhancer. Your role is to transform and refine user search queries to maximize the likelihood of retrieving the most accurate and comprehensive information from Google by increasing specificity and utilizing advanced search operators. The user's input could be a simple query or a complex one. If possible, incorporate advanced search operators such as "site:", "before:", "after:", "intitle:", etc., in your enhanced queries. Your goal is to present the refined query in JSON format."""
chat_model = ChatModel.from_pretrained("chat-bison@001")
parameters = {
    "temperature": 0.5,
    "max_output_tokens": 512,
    "top_p": 0.8,
    "top_k": 40
}
chat = chat_model.start_chat(
    context=context,
examples=[
    InputOutputTextPair(
        input_text="""{
      "userQuery": "latest Tesla electric cars"
    }""",
        output_text="""{
      "refinedQuery": "'Tesla' AND 'electric cars' site:tesla.com"
    }"""
    ),
    InputOutputTextPair(
        input_text="""{
      "userQuery": "Mars Rover recent discoveries"
    }""",
        output_text="""{
      "refinedQuery": "'Mars Rover' AND 'recent discoveries' site:nasa.gov"
    }"""
    ),
    InputOutputTextPair(
        input_text="""{
      "userQuery": "novel applications of quantum computing"
    }""",
        output_text="""{
      "refinedQuery": "'quantum computing' AND 'applications' site:arxiv.org"
    }"""
    ),
    InputOutputTextPair(
        input_text="""{
      "userQuery": "economic impact of COVID-19"
    }""",
        output_text="""{
      "refinedQuery": "'COVID-19' AND 'economic impact' source:worldbank"
    }"""
    ),
    InputOutputTextPair(
        input_text="""{
      "userQuery": "Oscar winning movies 2023"
    }""",
        output_text="""{
      "refinedQuery": "'Oscar winning' AND 'movies' AND '2023' site:imdb.com"
    }"""        
    ),
    InputOutputTextPair(
        input_text="""{
      "userQuery": "AI advancements in image recognition"
    }""",
        output_text="""{
      "refinedQuery": "'AI' AND 'advancements' AND 'image recognition' site:medium.com"
    }"""        
    ),
    InputOutputTextPair(
        input_text="""{
      "userQuery": "sustainable architecture trends"
    }""",
        output_text="""{
      "refinedQuery": "'sustainable architecture' AND 'trends' site:archdaily.com"
    }"""        
    )
]

)

def get_boosted_query(prompt):
    print('boosting')
    if not prompt:
        return ''

    input_json = {}
    input_json['userQuery'] = prompt
    
    response_text = chat.send_message(str(input_json)).text
    print('Response: ' + response_text)

    # Use regex to find the substring value of the refinedQuery key
    refined_query = get_refined_query(response_text)
   
    if refined_query:
        return refined_query
    else:
        return prompt

# Define this helper function
def get_refined_query(response_text):
    if not response_text:
        return ''
    
    # remove the leading "Response: {" and the trailing "}"
    response_text = response_text.lstrip('Response: {')
    response_text = response_text.rstrip('}')

    # use regex to find the refinedQuery and its value
    refined_query_match = re.search(r'"refinedQuery":\s*(".*?"|\'.*?\')', response_text)

    if refined_query_match:
        # get the refined query and remove the leading and trailing quotes
        refined_query = refined_query_match.group(1)
        
        return refined_query
    else:
        return ''