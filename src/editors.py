from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, ChatMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json


# Define the data structure of the article header which will contain the title and the SEO Keywords.
class ArticleHeaderFormatValidator(BaseModel):
    article_title: str = Field(description="Blog article title")
    seo_keywords: str = Field(description="SEO Keywords")

class ArticleChaptersFormatValidator(BaseModel):
    article_chapters: list = Field(description="Blog Article chapters")
    article_chapters_header: list = Field(description="Short description of the content")

class ArticleTextAfterReviewFormatValidator(BaseModel):
    article_text_consolidated: str = Field(description="Blog Article text after review from editor")
    #article_chapters_header: list = Field(description="Short description of the content")

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
                            When generating the chapter names, do not include "Chapter X" in the chapter title.
                            The chapters shall be enough to cover a 1500-2000 words article and they shall enable the reader to explore the topic of the article in details
                            For every chapter you must generate a brief description of its content, your target is the blog writer and your task is to give him a clear picture of what he has to write
                            You always keep in mind that SEO is everything. You think step by step"""
    
    _template_consolidation_system =   """You are editorGPT, a professional blog editor with many successful blogs running.
                                        Your output is always a JSON in the format specified by the user"""
    _template_consolidation_user =      """You take in inputs the article title and 5 seo keywords, the list of chapters, the list of chapters headers and the full article content.
                                        These were all written by you in a previous session. You read again the article carefully and double check it against the chapter titles and
                                        headers. You correct any errors and inconsistencies but make sure to mantain the same level of details.
                                        Feel free to add additional information to the article if needed or relevant
                                        You always make sure the blog article you receive in input is well formatted and around 2000 words.
                                        You always keep in mind that SEO is everything. You think step by step. 
                                        As a last step before before output the result you double check that the format is JSON, if not you correct it.
                                        These are the inputs: """

    #The PydanticOutputParser inject instructions into the prompt template to format the output as a JSON
    _parser_header = PydanticOutputParser(pydantic_object=ArticleHeaderFormatValidator)
    _parser_chapters = PydanticOutputParser(pydantic_object=ArticleChaptersFormatValidator)
    _parser_reviewed_article = PydanticOutputParser(pydantic_object=ArticleTextAfterReviewFormatValidator)

    def __init__(self, llm, article_topic):
        self._llm = llm
        self._article_topic = article_topic

    def _return_json_formatted_response(self, llm_response):
        llm_response_json = llm_response.to_json()
        return json.loads(llm_response_json["kwargs"]["content"])

    def generate_article_title_and_keywords(self, user_input_article_topic):
        prompt = ChatPromptTemplate(
        messages=[
            ChatMessagePromptTemplate.from_template(role = "system", template = self._template_title_and_keywords + "\n{format_instructions}"),
            HumanMessagePromptTemplate.from_template("{article_topic}")
        ],
        input_variables=["article_topic"],
        partial_variables={"format_instructions": self._parser_header.get_format_instructions()}
        )

        _input = prompt.format_prompt(article_topic=user_input_article_topic)
        llm_response = self._llm(_input.to_messages())
        llm_response_json = self._parser_header.parse(llm_response.content)
        return llm_response_json.article_title , llm_response_json.seo_keywords


    def generate_article_chapters(self, input_title, input_keywords):
        prompt = ChatPromptTemplate(
        messages=[
            ChatMessagePromptTemplate.from_template(role = "system", template = self._template_chapters + "\n{format_instructions}"),
            HumanMessagePromptTemplate.from_template("The article title is {article_title} and the SEO keywords are {seo_keywords}"),
        ],
        input_variables=["article_title", "seo_keywords"],
        partial_variables={"format_instructions": self._parser_chapters.get_format_instructions()}
        )

        _input = prompt.format_prompt(article_title=input_title, seo_keywords=input_keywords)
        llm_response = self._llm(_input.to_messages())
        llm_response_json = self._parser_chapters.parse(llm_response.content)
        return llm_response_json.article_chapters, llm_response_json.article_chapters_header
    
    def consolidate_article(self, article_title, article_keywords, article_chapters_list, article_chapters_header, article_chapters_content_list):
        
        article_content_before_review = '\n '.join(article_chapters_content_list)

        prompt = ChatPromptTemplate(
        messages=[
            ChatMessagePromptTemplate.from_template(role = "system", template = self._template_consolidation_system + "\n{format_instructions}"),
            HumanMessagePromptTemplate.from_template(self._template_consolidation_user +
                "Article title:{article_title}, SEO keywords: {seo_keywords}, Chapters: {article_chapters}, Chapters headers: {article_chapters_header}, Article: {article_content}"),
        ],
        input_variables=["article_title", "seo_keywords", "article_chapters", "article_chapters_header", "article_content"],
        partial_variables={"format_instructions": self._parser_reviewed_article.get_format_instructions()}
        )

        _input = prompt.format_prompt(article_title=article_title, seo_keywords=article_keywords, article_chapters=article_chapters_list, article_chapters_header=article_chapters_header, article_content=article_content_before_review)
        llm_response = self._llm(_input.to_messages())
        
        try:
            llm_response_json = self._parser_reviewed_article.parse(llm_response.content)
            article_content_after_review = llm_response_json.article_text_consolidated
        except :
            #sometimes gpt forget to return a json
            print("WARNING: JSON not returned, got value directly")
            article_content_after_review = llm_response.content
        
        return article_content_after_review