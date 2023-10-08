from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, ChatMessagePromptTemplate
#from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
#from langchain.llms import OpenAI

import os
import json

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


# Define the data structure of the article header which will contain the title and the SEO Keywords.
class ArticleHeaderFormatValidator(BaseModel):
    article_title: str = Field(description="Blog article title")
    seo_keywords: str = Field(description="SEO Keywords")

class ArticleChaptersFormatValidator(BaseModel):
    article_chapters: str = Field(description="Blog Article chapters")
    article_chapters_header: str = Field(description="Short description of the content")

class EditorGPT():
    _template_title_and_keywords =   """You are editorGPT, a professional blog editor with many successful blogs running. 
                                        You take in inputs the article topic and you generate a catchy title and a list of 5 keywords. 
                                        You always keep in mind that SEO is everything. You think step by step"""
    
    _template_chapters =   """You are editorGPT, a professional blog editor with many successful blogs running. 
                            You take in inputs the article title and 5 seo keywords. These were generated by you in a previous session and are given to you in json format.
                            Based on this information, you generate the chapters titles of the article. You shall always generate:
                            1. an introduction, explaining the topic of the article
                            2-n. the main body of the article
                            n+1. a conclusion
                            The chapters shall be enough to cover a 1500-2000 words article and they shall enable the reader to explore the topic of the article in details
                            For every chapter you must generate a brief description of its content, your target is the blog writer and your task is to give him a clear picture of what he has to write
                            You always keep in mind that SEO is everything. You think step by step"""
    
    #The PydanticOutputParser inject instructions into the prompt template to format the output as a JSON
    _parser_header = PydanticOutputParser(pydantic_object=ArticleHeaderFormatValidator)
    _parser_chapters = PydanticOutputParser(pydantic_object=ArticleChaptersFormatValidator)

    _article_title = ""
    _article_seo_keywords = ""

    def __init__(self, llm, article_topic):
        self.article_topic = article_topic

    def _return_json_formatted_response(self, llm_response):
        llm_response_json = llm_response.to_json()
        return json.loads(llm_response_json["kwargs"]["content"])
    
    def get_title(self):
        return self._article_title
    
    def get_seo_keywords(self):
        return self._article_seo_keywords

    def generate_article_title_and_keywords(self):
        prompt = ChatPromptTemplate(
        messages=[
            ChatMessagePromptTemplate.from_template(role = "system", template = self._template_title_and_keywords + "\n{format_instructions}"),
            HumanMessagePromptTemplate.from_template("{article_topic}")
        ],
        input_variables=["article_topic"],
        partial_variables={"format_instructions": self._parser_header.get_format_instructions()}
        )

        _input = prompt.format_prompt(article_topic=user_input_article_topic)
        llm_response = llm(_input.to_messages())
        llm_response_json = self._return_json_formatted_response(llm_response)
        self._article_title = llm_response_json["article_title"]
        self._article_seo_keywords = llm_response_json["seo_keywords"]


    def generate_article_chapters(self):
        prompt = ChatPromptTemplate(
        messages=[
            ChatMessagePromptTemplate.from_template(role = "system", template = self._template_chapters + "\n{format_instructions}"),
            HumanMessagePromptTemplate.from_template("The article title is {article_title} and the SEO keywords are {seo_keywords}"),
        ],
        input_variables=["article_title", "seo_keywords"],
        partial_variables={"format_instructions": self._parser_chapters.get_format_instructions()}
        )

        _input = prompt.format_prompt(article_title=self._article_title, seo_keywords=self._article_seo_keywords)
        llm_response = llm(_input.to_messages())
        llm_response_json = self._return_json_formatted_response(llm_response)
        return llm_response_json["article_chapters"], llm_response_json["article_chapters_header"]



llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_TEST_KEY"))
user_input_article_topic = "CAN Bus demo on Arduino"

blogself_editor = EditorGPT(llm, user_input_article_topic)

blogself_editor.generate_article_title_and_keywords()
article_chapters, article_headers = blogself_editor.generate_article_chapters()

article_title = blogself_editor.get_title()
article_seo_keywords = blogself_editor.get_seo_keywords()
print("Title: ", article_title)
print("SEO: ", article_seo_keywords)
print("Chapters: ", article_chapters)
print("Headers: ", article_headers)

#chapters = blogself_editor.generate_article_chapters()

#print(title_and_keywords)
#print(chapters)




# template_editorGPT = """You are editorGPT, a professional blog editor with many successful blogs running. 
#                         You take in inputs the article topic and you generate a catchy title and a list of 5 keywords. 
#                         You always keep in mind that SEO is everything. You think step by step"""



# llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_TEST_KEY"))

# prompt = ChatPromptTemplate(
#     messages=[
#     ChatMessagePromptTemplate.from_template(role = "system", template = template_editorGPT + "\n{format_instructions}"),
#     HumanMessagePromptTemplate.from_template("{article_topic}")
#     ],
#     input_variables=["article_topic"],
#     partial_variables={"format_instructions": parser.get_format_instructions()}
#     )

# _input = prompt.format_prompt(article_topic=user_input_article_topic)
# llm_response = llm(_input.to_messages())


# print(llm_response)

# Set up a parser + inject instructions into the prompt template.
#parser = PydanticOutputParser(pydantic_object=Joke)

# prompt = PromptTemplate(
#     template= template_editorGPT + "\n{format_instructions}\n{article_topic}\n",
#     input_variables=["article_topic"],
#     partial_variables={"format_instructions": parser.get_format_instructions()},
# )

# _input = prompt.format_prompt(article_topic=user_input_article_topic)

# output = llm(_input.to_string())

# parser.parse(output)

# prompt = ChatPromptTemplate.from_messages([
#     ("system", template_editorGPT),
#     ("human", "{article_topic}"),
#    ])

# template_bloggerGPT = """You are bloggerGPT, a professional blog write with many successful articles written. 
#                         Your task is to write an article with the title {article_title} using the SEO keywords: {article_seo_keywords}.
#                         You structure the blog article to be between 1000 and 1500 words long. It must be precise and detailed and contain practical examples if needed (coding, maths, etc depending on the topic).
#                         You write the article always with the following structure: 
#                         first an introduction, briefly explaing the topic and the next steps,
#                         then step by step instructions, as detailed as you can fill the max word length. If necessary you list pro and contra,
#                         then a conclusion summarizing what you have explained,
#                         finally a catchy call to action.
#                         Each section has to be separated by a subtitle, describing the content of the section
#                         You always keep in mind that SEO is everything. You think step by step, but you only always output the requested format"""

# prompt = ChatPromptTemplate.from_messages([
#     ("system", template_bloggerGPT)
#     ])

# chain = prompt | llm
# llm_response = chain.invoke({"article_title": "CAN Bus demo on Arduino", "article_seo_keywords": "CAN Bus, Arduino, Demo, Beginner's Guide, Communication"})

#print(llm_response)