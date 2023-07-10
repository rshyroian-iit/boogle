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
  "userQuery": "apple products"
}""",
            output_text="""{
  "refinedQuery": "intitle:\"apple\" ext:pdf site:apple.com after:2020-01-01"
}"""
        ),
        InputOutputTextPair(
            input_text="""{
  "userQuery": "effects of exercise on mental health"
}""",
            output_text="""{
  "refinedQuery": "intitle:\"exercise\" AND intitle:\"mental health\" -intitle:\"physical health\" filetype:pdf after:2015-01-01"
}"""
        ),

        InputOutputTextPair(
            input_text="""{
  "userQuery": "AI applications in healthcare"
}""",
            output_text="""{
  "refinedQuery": "intitle:\"AI\" AND intitle:\"healthcare\" (\"machine learning\" OR \"deep learning\") -intitle:\"finance\" site:nytimes.com"
}"""
        ),
        InputOutputTextPair(
            input_text="""{
  "userQuery": "Android versus iOS market share"
}""",
            output_text="""{
  "refinedQuery": "intitle:\"Android\" AND intitle:\"iOS\" AND intitle:\"market share\" -intitle:\"apps\" before:2022-01-01 source:statista"
}"""
        ),
        InputOutputTextPair(
            input_text="""{
  "userQuery": "effects of climate change on agriculture"
}""",
            output_text="""{
  "refinedQuery": "intitle:\"climate change\" AND intitle:\"agriculture\" -intitle:\"industry\" site:nature.com after:2018-01-01"
}"""        
        )
    ]
)