from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, ChatMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser, ResponseSchema
from pydantic import BaseModel, Field
import json

class ArticleChapterFormatValidator(BaseModel):
    article_chapter: str = Field(description="Blog article chapter content")


class WriterGPT():
    _template_role_writer =   """You are writerGPT, a professional blog writer with many successful blogs articles written. 
                                You take in inputs the article title, the SEO Keywords, the charpter lists, a brief description of each chapter and the content of 
                                the last chapter you have written.
                                Your task is to write the content of the chapter you receive in input by the user. The chapter is given to you as a number, representing the index
                                of the chapter in the chapter list, counting from 1.
                                Each chapter shall contain detailed information and practical examples if needed. Each chapter shall contain at least 2 paragraphs.
                                You always keep in mind that SEO is everything. You think step by step.
                                You MUST always output the content as JSON as described in the following lines: ."""
    
    _template_role_user = "Write me only the content of the chapter indicated by chapter index. Use the content of the last chapter you have written to give continuity to the article and avoid repetitions."

    _parser_article = PydanticOutputParser(pydantic_object=ArticleChapterFormatValidator)

    def __init__(self, llm):
        self._llm = llm

    def generate_article_chapter(self, input_title, input_seo_keywords, input_chapters_list, input_chapters_header_list, input_chapter_index, last_chapter_text):
        
        format_instructions = self._parser_article.get_format_instructions()
        
        prompt = ChatPromptTemplate(
        messages=[
            ChatMessagePromptTemplate.from_template(role = "system", template = self._template_role_writer + "\n{format_instructions}"),
            HumanMessagePromptTemplate.from_template("Title: {article_title}, SEO Keywords: {seo_keywords}, Chapters: {chapters_list}, Chapters headers: {chapters_header_list}, Chapter index: {chapter_index}, Last Chapter content: {last_chapter_content}." 
                                                     + self._template_role_user)
        ],
        input_variables=["article_title", "seo_keywords", "chapters_list", "chapters_header_list", "chapter_index", "last_chapter_content"],
        partial_variables={"format_instructions": format_instructions}
        )

        _input = prompt.format_prompt(article_title=input_title, seo_keywords=input_seo_keywords, chapters_list=input_chapters_list, 
                                      chapters_header_list=input_chapters_header_list, chapter_index=input_chapter_index, last_chapter_content=last_chapter_text)
        
        llm_response = self._llm(_input.to_messages())
        llm_response_json = self._parser_article.parse(llm_response.content)
        return llm_response_json.article_chapter