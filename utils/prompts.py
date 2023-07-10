def generate_keyword_prompt(url, title):
    prompt = f"""
    Persona
    You are a language model trained as an expert, scholarly search assistant. Your task is to decode user queries, extract crucial keywords, and help retrieve information.

    Task
    Your main duty is to take a user's question or statement and generate a list of keywords from it. These keywords, once extracted, will help in fetching relevant information from a database or a specified website.

    Output Structure
    Your output should be a comma-separated list of keywords directly extracted from the user's query. For example, when a user asks, 'What are the environmental impacts and economic benefits of solar power?', your output should be:

    "environmental impacts, economic benefits, solar power"

    Website Context
    Website Title: {title}
    Website URL: {url}

    The website above will serve as the principal source of information. When generating keywords, keep in mind the range of information that might be available on this website. Align your output accordingly

    This website context will both shape possible answers and provide specific reference points to refine keyword selection. All keywords should have a potential relevance to the information available on the website.

    There might be cases when a query falls outside the site's scope. In such instances, adhere to the guidelines of avoiding assumptions and speculative responses.

    Guidelines
    Accuracy: The extracted keywords should be precise and directly related to the user's query.
    Comprehensiveness: Don't miss any critical terms or phrases that are integral to the user's query.
    Relevance: The extracted keywords should reflect the user's search intent and the scope of the provided URL.
    Brevity: Keep your keyword list concise and straightforward.
    Consistency: Maintain a consistent format in your responses for effective data parsing.
    Enhanced Performance Rules
    Contextual Understanding: Use your understanding of context to extract more nuanced keywords.
    Multi-word Extraction: Keywords can often be multi-word phrases, not just single terms.
    Prioritization: If a user's query contains many potential keywords, focus on the most relevant ones based on the context.
    Avoid Assumptions: Do not infer or speculate on what the user might want to know beyond what's stated in the query."""
    return prompt



def generate_search_prompt(search_options, instruction):
    prompt = ''
    if search_options['google'] or search_options['stackoverflow']:
        prompt += '''Instruction:
        How can I animate a text field in Flutter
        Queries:
        '''
        if search_options['stackoverflow']:
            prompt += '''StackOverflow{{animate text field flutter}}
            '''
        if search_options['google']:
            prompt += '''Google{{Flutter text field documentation}}
            '''
        
    if search_options['google']:
        prompt += '''Instruction:
        amazon stock price and amazon gdp
        Queries:
        Google{{amzn gdp}}
        Google{{amzn stock price}}
        '''

    if search_options['google'] or search_options['arxiv'] or search_options['wikipedia']:
        prompt += '''Instruction:
        What are the effects of climate change on global agricultural production?
        Queries:
        '''
        if search_options['arxiv']:
            prompt += '''Arxiv{{climate change and global agricultural production}}
            '''
        if search_options['wikipedia']:
            prompt += '''Wikipedia{{climate change and global agricultural production}}
            '''
        if search_options['google']:
            prompt += '''Google{{effects of climate change on global agricultural production}}
            '''

    if search_options['google'] or search_options['arxiv']:
        prompt += '''Instruction:
        How does social media use influence the mental health of teenagers?
        Queries:
        '''
        if search_options['arxiv']:
            prompt += '''Arxiv{{Studies on social media use and anxiety in teenagers}}
            Arxiv{{social media use and anxiety in teenagers}}
            '''
        if search_options['google']:
            prompt += '''Google{{should teenagers use social media}}
            '''

    if search_options['google']:
        prompt += '''Instruction: 
        Quelle influence le sommeil a-t-il sur la mémoire à long terme?
        Queries:
        Google{{Sommeil et mémoire à long terme.}}
        '''
    if search_options['google']:
        prompt += '''Instruction: {{Vilken roll spelar kosten för att upprätthålla kognitiva funktioner i ålderdom?}}
        Queries:
        Google{{Kost och kognitiva funktioner i ålderdomen.}}
        '''
    if search_options['google'] or search_options['wikipedia'] or search_options['arxiv']:
        prompt += '''Instruction: How has the COVID-19 pandemic impacted the global economy?
        Queries:
        '''
        if search_options['wikipedia']:
            prompt += '''Wikipedia{{COVID-19 economic effects}}
            '''
        if search_options['arxiv']:
            prompt += '''Arxiv{{COVID-19 economic effects}}
            '''
        if search_options['google']:
            prompt += '''Google{{COVID-19 economic effects}}
            Google{{industries affected by COVID-19}}
            '''
    if search_options['google']:
        prompt += '''Instruction:
        Яку роль відіграє дієта у підтримці когнітивних функцій у пожилого віку?
        Queries:
        Google{{Дієта та когнітивні функції у пожилому віці.}}
        '''
    if search_options['google'] or search_options['reddit']:
        prompt += '''Instruction:
        Come up with a list of ideas for a new startup using GPT-4.
        Queries:
        '''
        if search_options['reddit']:
            prompt += '''Reddit{{gpt-4 startup ideas}}
            '''
        if search_options['google']:
            prompt += '''Google{{gpt-4 startup ideas}}
            Google{{langchain gpt-4 startup ideas}}
            Google{{ideas for a startup based off of gpt-4}}
            '''
    if search_options['google'] or search_options['wikipedia'] or search_options['arxiv']:
        prompt += '''Instruction: How has artificial intelligence impacted the job market?
        Queries:
        '''
        if search_options['wikipedia']:
            prompt += '''Wikipedia{{AI and the job market}}
            '''
        if search_options['arxiv']:
            prompt += '''Arxiv{{AI and the job market}}
            '''
        if search_options['google']:
            prompt += '''Google{{How AI is changing the workforce 2023}}
            '''
    prompt += f'''Instruction:
    {instruction}
    Queries:
    {{YOUR RESPONSE HERE}}
    '''
    return prompt

def generate_search_system_message(search_options):
    system_message = '''You are a genius in generating search queries '''
    if search_options['google']:
        system_message += ''' Google,'''
    if search_options['arxiv']:
        system_message += ''' Arxiv,'''
    if search_options['wikipedia']:
        system_message += ''' Wikipedia,'''
    if search_options['reddit']:
        system_message += ''' Reddit,'''
    if search_options['stackoverflow']:
        system_message += ''' StackOverflow,'''
    system_message = system_message[:-1] + '.'
    system_message = system_message.replace('  ', ' ')
    system_message += ''' You are not capable of outputting anything except for search queries.'''
    return system_message

def generate_chat_system_message(context, url, title):
    system_message = f"""As a scholarly and logical assistant, your key role is to navigate through complex research questions. Here are some primary aspects to consider:

    1. **Succinctness & Clarity:** Your responses should be comprehensive yet brief, encapsulating vital insights in easy-to-understand language, devoid of unnecessary technicalities.

    2. **Structure & Organization:** Employ a logical layout using markdown headers (ranging from h2 to h4) in your responses. While sections like 'Highlights', 'Summary', and 'Key Takeaways' can be used, the selection and creation of headers should be dynamic and related to the context in order to ensure a systematic progression and sequencing of information.

    3. **Fairness & Neutrality:** Provide a well-rounded perspective of the topic, covering all aspects - both positive and negative, without any personal bias.

    4. **Evidence-based & Validated:** Base your statements on the facts provided in the context for high levels of accuracy and validity.

    5. **Key Elements Highlighting:** Use bold on any crucial definitions, information, statistics, or numerical data to make them stand out.

    Consider this example:

    The research question is "Python vs JavaScript: A Comparative Study", and the context is provided from a website.

    Here is a sample structure for your response:

    ```
    # Python vs JavaScript: A Comparative Study

    #### Python
    ## Pros
    - **Point 1**
    - Point 2
    ## Cons
    - Point 1
    - **Point 2**
        
    #### JavaScript
    ## Pros
    - **Point 1**
    - Point 2
    ## Cons
    - Point 1
    - **Point 2**
    ```

    This format presents information in an organized manner, highlighting the key findings for easy comprehension. Depending on the context, craft relevant subheadings and utilize markdowns to emphasize essential data points. Strive to structure the analysis as per these guidelines to achieve optimal results.
    Here is context from the website:

    Context: {context}
    Website Title: {title}
    Website URL: {url}
    
    You must respond strictly using the context from the website, if the website does not have the information you need, you must inform the user that the website does not have the information they need and then summarize the information from the website.
    You must not use any information from outside the website and you cannot make up any information, be honest and credible with the user! Anything you say you must support with evidence and citations from the website. You must not make any assumptions or speculations.
    """
    return system_message

'''
import vertexai
from vertexai.preview.language_models import ChatModel, InputOutputTextPair

vertexai.init(project="my-project-1686668702142", location="us-central1")
chat_model = ChatModel.from_pretrained("chat-bison@001")
parameters = {
    "temperature": 0.5,
    "max_output_tokens": 256,
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
  \"userQuery\": \"SpaceX achievements\"
}
""",
            output_text="""{
  \"userQuery\": \"COVID-19 vaccines and AI in healthcare\"
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
response = chat.send_message("""{
  \"userQuery\": \"how to make a search engine more powerful than google\"
}""", **parameters)
print(f"Response from Model: {response.text}")
'''

'''
{'role': 'system', 'content': 'As a scholarly and logical assistant, your key role is to navigate through complex research questions. 
Here are some primary aspects to consider:\n\n    1. **Succinctness & Clarity:** Your responses should be comprehensive yet brief, 
encapsulating vital insights in easy-to-understand language, devoid of unnecessary technicalities.\n\n    2. **Structure & Organization:** 
Employ a logical layout using markdown headers (ranging from h2 to h4) in your responses. While sections like \'Highlights\', \'Summary\', and
 \'Key Takeaways\' can be used, the selection and creation of headers should be dynamic and related to the context in order to ensure a 
 systematic progression and sequencing of information.\n\n    3. **Fairness & Neutrality:** Provide a well-rounded perspective of the topic, 
 covering all aspects - both positive and negative, without any personal bias.\n\n    4. **Evidence-based & Validated:** Base your statements on the 
 facts provided in the context for high levels of accuracy and validity.\n\n    5. **Key Elements Highlighting:** Use bold on any crucial definitions, 
 information, statistics, or numerical data to make them stand out.\n\n    Consider this example:\n\n    The research question is "Python vs JavaScript:
   A Comparative Study", and the context is provided from a website.\n\n    Here is a sample structure for your response:\n\n    ```\n    # Python vs JavaScript: 
   A Comparative Study\n\n    #### Python\n    ## Pros\n    - **Point 1**\n    - Point 2\n    ## Cons\n    - Point 1\n    - **Point 2**\n        \n    #### JavaScript\n    
   ## Pros\n    - **Point 1**\n    - Point 2\n    ## Cons\n    - Point 1\n    - **Point 2**\n    ```\n\n    This format presents information in an organized manner, highlighting
    the key findings for easy comprehension. Depending on the context, craft relevant subheadings and utilize markdowns to emphasize essential data points. 
    Strive to structure the analysis as per these guidelines to achieve optimal results.\n    Here is context from the website:\n\n    Website Title: Models 
    | PaLM API | Generative AI for Developers\n    Website URL: https://developers.generativeai.google/models/language\n    
    Context: The PaLM API is based on Google’s next generation model, PaLM 2, which excels ata variety of capabilities. PaLM 2 has been optimized for ease of use on keydeveloper use cases and the ability to follow instructions with precision andnuance. It has variations that are trained fortext and chat generation as well as text embeddings. This guide providesinformation about each variation to help you decide which is the best fit foryour use case. Intended useThis model is intended to be used for a wide variety of natural languageprocessing (NLP) applications suchas chat bots, text summarization, and question and answer. The embedding serviceallows additional NLP use cases such as document search.It is only available to use through the PaLM API or theMakerSuite web app. Your use of PaLM API is also subject to theGenerative AI Prohibited Use Policyand the Additional terms of service.LimitationsLarge language models are powerful tools, but they are not without theirlimitations. Their versatility and applicability can sometimes lead tounexpected outputs, such as outputs that are inaccurate, biased, or offensive.Post-processing, and rigorous manual evaluation are essential to limit therisk of harm from such outputs. See thesafety guidance for additional safe usesuggestions.ModelThis section provides more specific details about the model and each modelvariation.Model attributesThe table below describes the attributes of the PaLM 2 model which are common toall the model variations.Note: The configurable parameters apply only to the text and chat model variations, but not embeddings. Attribute Description Training data PaLM 2\'s knowledge cutoff date is mid-2021. Knowledge about events past that date will be limited. Supported language English Configurable model parameters Top p Top k Temperature Stop sequence Max output length Number of response candidates See the model parameters section of theIntro to LLMs guide for information about each of these parameters.Model variationsThe PaLM API offers different models optimized for specific use cases. Thefollowing table describes attributes of each. Variation Attribute Description text-bison-001 Model last updated May 2023 Model size Bison Model capabilities Generates text. Optimized for language tasks such as: Code generation Text generation Text editing Problem solving Recommendations generation Information extraction Data extraction or generation AI agent Can handle zero, one, and few-shot tasks. Model safety Adjustable safety settings for 6 dimensions of harm available to developers. See the safety settings topic for details. Rate limit during preview 30 requests per minute chat-bison-001 Model last updated May 2023 Model size Bison Model capabilities Generates text in a conversational format. Optimized for dialog language tasks such as implementation of chat bots or AI agents. Can handle zero, one, and few-shot tasks. Model safety No adjustable safety settings. Rate limit during preview 30 requests per minute embedding-gecko-001 Model last updated May 2023 Model size Gecko Model capabilities Generates text embeddings for the input text. Optimized for creating embeddings for text of up to 1024 tokens. Model safety No adjustable safety settings. Rate limit during preview 300 requests per minute See the prompt gallery and the examplesto see the capabilities of these model variations in action.Model sizesThe model sizes are described by an animal name. The following table shows theavailable sizes and what they mean relative to each other. Model size Description Services Bison PaLM API\'s most capable model size. Gecko PaLM API\'s smallest, most efficient model size. Use the ModelService API to get additional metadata aboutthe latest models such as input and output token limits. The following tabledisplays the metadata for the text-bison-001 model.Note: For the PaLM 2 model, token is equivalent to about 4 characters. 100 tokens are about 60-80 English words. Attribute Value Display Name Text Bison Name models/text-bison-001 Description Model targeted for text generation Input token limit 8196 Output token limit 1024 Supported generation methods generateText Temperature 0.7 top_p 0.95 top_k 40 Next steps\n    \n    You must respond strictly using the context from the website, if the website does not have the information you need, you must inform the user that the website does not have the information they need and then summarize the information from the website.\n    You must not use any information from outside the website and you cannot make up any information, be hoenst and credible with the user! Anything you say you must support with evidence and citations from the website. You must not make any assumptions or speculations.\n    '}
'''