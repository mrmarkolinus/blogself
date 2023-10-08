from langchain.chat_models import ChatOpenAI
from editors import EditorGPT
import os

class BlogArticle():
    
    def __init__(self, llm, article_topic, workers):
        self._llm = llm
        self._workers = workers
        self._article_topic = article_topic

        self._editor = self._workers["editor"](self._llm, self._article_topic)

        self._article_title, self._article_seo_keywords = self._editor.generate_article_title_and_keywords(self._article_topic)
        self._article_chapters, self._article_chapters_header = self._editor.generate_article_chapters(self._article_title, self._article_seo_keywords)

    def get_title(self):
        return self._article_title
    
    def get_seo_keywords(self):
        return self._article_seo_keywords
    
    def get_chapters(self):
        return self._article_chapters
    
    def get_chapters_headers(self):
        return self._article_chapters_header
    
    def get_overview(self):
        overview_str = "Title: " + self._article_title + "\n---------\n" + "Chapters: " + ', '.join(self._article_chapters) + "\n---------\n" + "Chapters headers: "
        overview_str += ', '.join(self._article_chapters_header) + "\n---------\n" + self._article_seo_keywords
        return overview_str

llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_TEST_KEY"))
user_input_article_topic = "CAN Bus demo on Arduino"

workers = {}
workers["editor"] = EditorGPT

blogself = BlogArticle(llm, user_input_article_topic, workers)
print(blogself.get_overview())
