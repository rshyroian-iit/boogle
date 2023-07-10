from vertexai.preview.language_models import TextEmbeddingModel
import google.cloud.aiplatform as aiplatform
from vertexai.preview.language_models import ChatModel, InputOutputTextPair, ChatMessage
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import vertexai
import json  # add this line
from google.oauth2 import service_account
import numpy as np

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

model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")


def gecko_embedding(string):
    embedding = model.get_embeddings([string])
    embedding_vector = embedding[0].values
    return embedding_vector
    #return embeddings

def get_default_embedding():
    # create default embedding
    #default_embedding = gecko_embedding(['None'])
    #np.save('utils/default_embedding_gecko.npy', default_embedding)

    # check if default embedding exists
    default_embedding = np.load('utils/default_embedding_gecko.npy')
    #print(type(default_embedding))
    return default_embedding


def embedding_function(text, num_retries=0):
    print(num_retries)
    embedding = None
    if text == '':
        return get_default_embedding()
    try: 
        embedding = gecko_embedding(text)
    except Exception as e:
        print(f'Error in embedding_function: {e}')
        embedding = None
    if embedding is None:
        if num_retries < 3:
            embedding = embedding_function(text, num_retries + 1)
        else:
            print(f'Error in embedding_function: embedding is None. Returning default embedding.')
            embedding = get_default_embedding()
    return embedding

if __name__ == '__main__':
    print(get_default_embedding())