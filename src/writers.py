from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, ChatMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json

class ArticleChapterFormatValidator(BaseModel):
    article_chapter: str = Field(description="Blog article chapter content")


class WriterGPT():
    _template_role_writer =   """You are writerGPT, a professional blog writer with many successful blogs articles written. 
                                You always keep in mind that SEO is everything. You think step by step.
                                You MUST always output the content as JSON as described in the following lines: ."""
    
    _template_role_user = """You take in inputs the article title, the SEO Keywords, the chapter to write and its brief description
                            Your task is to write the content of the chapter you receive in input. 
                            The chapter shall contain detailed information and practical examples if needed.
                            Write at least 2 paragraphs, the more the better, fill the chapter of details and examples (if needed).
                            After writing the chapter content, read it again. Check carefully if there are any errors or information missing. If so please correct it.
                            Think step by step, your output MUST always be a JSON.
                            As a last step before before output the result you double check that the format is JSON, if not you correct it.
                            Here are the inputs:
                            """

    _parser_article = PydanticOutputParser(pydantic_object=ArticleChapterFormatValidator)

    def __init__(self, llm):
        self._llm = llm

    def generate_article_chapter(self, input_title, input_seo_keywords, input_chapters_list, input_chapters_header_list, input_chapter_index, last_chapter_text):
        
        format_instructions = self._parser_article.get_format_instructions()
        
        prompt = ChatPromptTemplate(
        messages=[
            ChatMessagePromptTemplate.from_template(role = "system", template = self._template_role_writer + "\n{format_instructions}"),
            HumanMessagePromptTemplate.from_template(self._template_role_user + 
                                                     "Title: {article_title}, SEO Keywords: {seo_keywords}, Chapter: {current_chapter}, Chapters header: {current_chapter_header}.")
        ],
        input_variables=["article_title", "seo_keywords", "current_chapter", "current_chapter_header"],
        partial_variables={"format_instructions": format_instructions}
        )

        _input = prompt.format_prompt(article_title=input_title, seo_keywords=input_seo_keywords, current_chapter=input_chapters_list[input_chapter_index], 
                                      current_chapter_header=input_chapters_header_list[input_chapter_index])
        
        llm_response = self._llm(_input.to_messages())
        try:
            llm_response_json = self._parser_article.parse(llm_response.content)
            article_chapter_content = llm_response_json.article_chapter
        except:
        # #except json.decoder.JSONDecodeError as e:
        #     #sometimes gpt forget to return a json
        #     try:
            print("WARNING: JSON not returned, got value directly")
            article_chapter_content = llm_response.content
        #     except OutputParserException as ope:
        #         print("WARNING: JSON not returned, got value directly")
        #         article_chapter_content = llm_response.content

        return article_chapter_content