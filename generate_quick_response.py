from vertexai.language_models import TextGenerationModel
import google.cloud.aiplatform as aiplatform
from vertexai.preview.language_models import ChatModel, InputOutputTextPair, ChatMessage
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import vertexai
import json  # add this line
from google.oauth2 import service_account
from ast import literal_eval


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

model = TextGenerationModel.from_pretrained("text-bison")
def get_quick_response(query, background):
    default_prompt = """You are a Google Search Assistant. Your task is to give a detailed response to the user. To perform this, you will be provided with a set of background information. You must formulate your answer utilizing the information presented to you there.

Search Query: {}

Background: {}

Response: """.format(query, background)
    print('Getting resopnse...')
    response = model.predict(default_prompt, max_output_tokens=256)
    print('Got response!')
    return response.text




