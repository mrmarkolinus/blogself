from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, ChatMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json

class ArticleChapterFormatValidator(BaseModel):
    article_chapter: str = Field(description="Blog article chapter content")


class WriterGPT():
    _template_role_writer =   """You are writerGPT, a professional blog writer with many successful blogs articles written.
                                You always reply in JSON format as described in the following lines."""
    
    _template_role_user = """I. Your Role
                            Your role is to generate the content for the chapter based on the inputs provided and ensure that it is detailed, accurate, and well-structured. 
                            You will also perform a final review to check for errors and correct the format if necessary.
                            II. Context and Topic:
                            The context is writing a chapter for a specific topic.
                            Article Title: [Article Title]
                            SEO Keywords: [SEO Keywords]
                            Chapter: [Chapter]
                            Brief Description: [Brief Description]
                            III. Task description
                            The task is to write the content of the chapter based on the inputs provided. The content should be detailed and include practical examples if needed.
                            Practical Examples can be detailed code, tables, graphs, etc.
                            IV. Subtask Sequence:
                            1. Read the article title, SEO keywords, chapter title, and its brief description.
                            2. Write at least 5 paragraphs of detailed content for the chapter.
                            3. Review the written content for errors or missing information.
                            4. Correct any errors found and ensure the content is well-structured.
                            5. Double-check that the format of the final output is JSON.
                            V. Output Format:
                            The output should be a JSON format containing the written content of the chapter.
                            VI. Constraints or Requirements:
                            The content should be detailed and well-structured. It should include practical examples if needed. The final output format should be JSON.
                            """
    
    
    
    # """You take in inputs the article title, the SEO Keywords, the chapter to write and its brief description
    #                         Your task is to write the content of the chapter you receive in input. 
    #                         The chapter shall contain detailed information and practical examples if needed.
    #                         Write at least 2 paragraphs, the more the better, fill the chapter of details and examples (if needed).
    #                         After writing the chapter content, read it again. Check carefully if there are any errors or information missing. If so please correct it.
    #                         Think step by step, your output MUST always be a JSON.
    #                         As a last step before before output the result you double check that the format is JSON, if not you correct it.
    #                         Here are the inputs:
    #                         """

    _parser_article = PydanticOutputParser(pydantic_object=ArticleChapterFormatValidator)

    def __init__(self, llm):
        self._llm = llm

    def generate_article_chapter(self, input_title, input_seo_keywords, input_chapters_list, input_chapters_header_list, input_chapter_index, last_chapter_text):
        
        format_instructions = self._parser_article.get_format_instructions()
        user_chapter_prompt = str.replace(self._template_role_user, "[Article Title]", input_title)
        user_chapter_prompt = str.replace(user_chapter_prompt, "[SEO Keywords]", input_seo_keywords)
        user_chapter_prompt = str.replace(user_chapter_prompt, "[Chapter]", input_chapters_list[input_chapter_index])
        user_chapter_prompt = str.replace(user_chapter_prompt, "[Brief Description]", input_chapters_header_list[input_chapter_index])

        prompt = ChatPromptTemplate(
        messages=[
            ChatMessagePromptTemplate.from_template(role = "system", template = self._template_role_writer + "\n{format_instructions}"),
            HumanMessagePromptTemplate.from_template(user_chapter_prompt)
        ],
        input_variables=[],
        partial_variables={"format_instructions": format_instructions}
        )

        _input = prompt.format_prompt()
        
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