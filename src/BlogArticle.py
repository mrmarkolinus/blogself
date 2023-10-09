from langchain.chat_models import ChatOpenAI
from editors import EditorGPT
from writers import WriterGPT
import os
import logging

class BlogArticle():
    
    def __init__(self, llm, article_topic, workers, log_obj):
        self._llm = llm
        self._workers = workers
        self._article_topic = article_topic

        self._editor = self._workers["editor"](self._llm, self._article_topic)
        self._writer = self._workers["writer"](self._llm)

        self._article_title, self._article_seo_keywords = self._editor.generate_article_title_and_keywords(self._article_topic)
        log_obj.info("Article title: " + self._article_title)
        log_obj.info("Artcicle keywords: " + self._article_seo_keywords)

        self._article_chapters, self._article_chapters_header = self._editor.generate_article_chapters(self._article_title, self._article_seo_keywords)
        log_obj.info("Article chapters: " + ', '.join(self._article_chapters))
        log_obj.info("Article chapters headers: " + ', '.join(self._article_chapters_header))

        self._chapter_content = []
        last_chapter_content = " "

        for (index, _) in enumerate(self._article_chapters):
            self._chapter_content.append(self._writer.generate_article_chapter(self._article_title, self._article_seo_keywords, 
                                                                               self._article_chapters, self._article_chapters_header, index + 1,
                                                                               last_chapter_content))
            last_chapter_content = self._chapter_content[index]
            log_obj.info("Chapter \"" + self._article_chapters[index] + "\" generated successfully")
            log_obj.info(self._chapter_content[index])


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

    def get_article(self):
        formatted_article = self._article_title
        formatted_article += "\n---------\n"

        for index, chapter in self._article_chapters:
            formatted_article += chapter + "\n---------\n"
            formatted_article += self._chapter_content[index]
            formatted_article += "\n---------\n"

        return formatted_article

workers = {}
workers["editor"] = EditorGPT
workers["writer"] = WriterGPT

# Configure the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)

# Configure the log format
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('blogself')

logger.info("Contacting OpenAI")

llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_TEST_KEY"), temperature=0)
user_input_article_topic = "Minecraft developement history"

logger.info("Creating the blog article frin topic: " + user_input_article_topic) 
blogself = BlogArticle(llm, user_input_article_topic, workers, logger)
print(blogself.get_overview())
#print(blogself.get_article())
