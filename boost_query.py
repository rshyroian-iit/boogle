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
#with open(
#    "service_account.json"
#) as f:  # replace 'serviceAccount.json' with the path to your file if necessary
#    service_account_info = json.load(f)
service_account_info = literal_eval("""
                                      "type": "service_account",
                                      "project_id": "ghc-028",
                                      "private_key_id": "ab6356d3f227cf640d647c9eb72467d1927808b6",
                                      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCtfEPb4mDhxJzt\nUVDPMYIdeX+s/uKCAEYPUUYSnKRG9Q85szv9YSbb3gDYzzzzk2gWhr62Cn5IB7oh\nWodFe7Y9sp5xYTf4SEDZ4V8wLQpjArWUXuqhBUQTbFuE3MAGdjgNxZITe2zem7tt\n+JSOCtgqU1VDuUWs/8hL5NHr4aBGYwPnWXqfNwW7rEVUx/FCRn3gZvEdjCjrAw06\n82JT6IygQV81HVxH7RwAsAVSUD6mEH/g6zsqi3dyWLDhCfX31jIqW37NMRIRHdqY\nMGAdpPbzLkTauOfY+BK5u+o0CLeitRSHUwvtWgvxlYQxbMCmK9hslMyeazGRsX6t\nwmrsF+19AgMBAAECggEACDMS2/4nmRQbXKYWvSw4W59F9w228/ECXq/3MWMA6q+j\ncBU2FSQ123dzL8wfs914MnRc6Cq3zDy9Qd1O/mw58VGTZoVzSUNU+VdLEfJXBtX2\nchRIX6LplEdvTejHFKcawB/h5xTS0PSoV6rDjrEZhWqZ4ZEMp4ARXfDrMQxhcGIi\nhWTMJOfWStJ3Gx00ovaKbTJ5hEOL4XUKhlVx/3MgrbsWCdQh3GTIs1BrxU5zMgPL\nVqBYhOx7Xrw6eWaed4lvrpekQisjZDtq2XFdLa5PtJMA8Kdu25Vp1QHhjuFrlVip\n0XMMw/iwusPJzixgY5CZD9WNby+MFV7OgQjiXWV+AQKBgQD0gR87iEzI+bYYWpcf\n/iDVyrdzpnUM6fbg73cE+IBOGmjbAEvGf7+oUG76xg4eNfGk0RkZF2by9SpZfq9w\nTzK8jMXbHpQX5aHEL2wrvksE60HouOG7ubBrh5TRLkwKKNB07K4Pb12HVI1DHbv6\nwfcnOsj5CAHUdE/9mgYoblu+fQKBgQC1pFoalX2p6+zXrcHs5dT16zaEosOfqTMv\nHX676gvK6TUPJLrM0qlqQjL78RxwfBrxLS/NQaG0MymHzgkK9LktdkzhegRICMnk\nqsiy5to5MyFrFAyFLFtpq+p4dVqennGwVLHHY7VM/tgGEeYIt3QSedrtxF1wtYCX\nCHaYq0kbAQKBgQDEWeVRE7ZGN3Lqv+VZReXsiq0kbOrXAhTGssfr7/xpvH+0T9qK\ngBDUBDP7o4226S8zYtA6/DYqqoPl9vzAvnlKPequezIGttxgBo1h26G3Q45cbAyr\niwWIdQsnqXxbNEejfmaR8qczhM0ktv489AOdN3IpuyptCTMrv8NuOKHoqQKBgFC3\nlz7G/Y+8AoSZd1rRi0A45QIt3iaeJtuiDMZurAzgcy6mkMgiORy6DDP/IjcuPz67\naMmah8QvFB6ARW5z77IvJtzvvuVP2n/eEM/HXGQcv5X409N+MaUUu14KMFnaaQUF\nrfa/7Too6VBRNdrbwx3OvqX4I9nJHjp/jUwsmZEBAoGBAJD6jl7FruJLF5h0j0CW\nMe5Dam8o85g7MPLIdH0/RxgVHKK0HrGVd0ewsBGudBcCYhw4woIxDFxvwrakM1+L\nBYDfaCBNvBcPYZgOZ94oC6QnkRHSV1bVw3T9Fxlyn/4tASS5qlnFhz+Y0lgGMNlm\nwdytoCAoVQfQ0sfYqK1uIWAS\n-----END PRIVATE KEY-----\n",
                                      "client_email": "participant-sa-11@ghc-028.iam.gserviceaccount.com",
                                      "client_id": "116494781324332838592",
                                      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                      "token_uri": "https://oauth2.googleapis.com/token",
                                      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/participant-sa-11%40ghc-028.iam.gserviceaccount.com",
                                      "universe_domain": "googleapis.com"
                                      """)

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