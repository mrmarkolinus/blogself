from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, ChatMessagePromptTemplate
#from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
#from langchain.llms import OpenAI

import os

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


# Define the data structure of the article header which will contain the title and the SEO Keywords.
class ArticleHeader(BaseModel):
    artitcle_title: str = Field(description="Blog article title")
    seo_keywords: str = Field(description="SEO Keywords")

class EditorGPT():
    _template_title_and_keywords =   """You are editorGPT, a professional blog editor with many successful blogs running. 
                                        You take in inputs the article topic and you generate a catchy title and a list of 5 keywords. 
                                        You always keep in mind that SEO is everything. You think step by step"""
    
    #The PydanticOutputParser inject instructions into the prompt template to format the output as a JSON
    _parser = PydanticOutputParser(pydantic_object=ArticleHeader)

    def __init__(self, llm, article_topic):
        self.article_topic = article_topic

    def generate_article_title_and_keywords(self):
        prompt = ChatPromptTemplate(
        messages=[
            ChatMessagePromptTemplate.from_template(role = "system", template = self._template_title_and_keywords + "\n{format_instructions}"),
            HumanMessagePromptTemplate.from_template("{article_topic}")
        ],
        input_variables=["article_topic"],
        partial_variables={"format_instructions": self._parser.get_format_instructions()}
        )

        _input = prompt.format_prompt(article_topic=user_input_article_topic)
        return llm(_input.to_messages())

    def generate_article_chapters(self):
        pass


llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_TEST_KEY"))
user_input_article_topic = "CAN Bus demo on Arduino"

blogself_editor = EditorGPT(llm, user_input_article_topic)

print(blogself_editor.generate_article_title_and_keywords())




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