from langchain.chat_models import ChatOpenAI
from editors import EditorGPT
from writers import WriterGPT
from BlogCache import BlogCache
import os
import logging

class BlogArticle():
    
    def __init__(self, llm, article_topic, workers, log_obj, load_from_cache_if_possible=True, article_file_path = "src/.output/article.txt"):
        self._llm = llm
        self._workers = workers
        self._article_topic = article_topic
        self._logger = log_obj

        self._editor = self._workers["editor"](self._llm, self._article_topic)
        self._writer = self._workers["writer"](self._llm)

        self._cache = BlogCache(load_from_cache_if_possible)

        self._generate_title_and_seo()
        self._generate_chapters_title_and_description()
        self._generate_chapters()
        
        self._article_text_consolidated = self._editor.consolidate_article(self._article_title, self._article_seo_keywords, self._article_chapters, self._article_chapters_header, self._chapter_content)

        with open(article_file_path, "w") as article_file:
            article_file.write(self._article_text_consolidated)

    def _generate_title_and_seo(self):

        if self._cache.is_article_title_cached() and self._cache.is_article_seo_keywords_cached():
            self._article_title = self._cache.get_cached_article_title()
            self._article_seo_keywords = self._cache.get_cached_article_seo_keywords()
            self._logger.info("Article title [LOADED FROM CACHE]: " + self._article_title)
            self._logger.info("Artcicle keywords [LOADED FROM CACHE]: " + self._article_seo_keywords)
        else:
            self._article_title, self._article_seo_keywords = self._editor.generate_article_title_and_keywords(self._article_topic)
            self._logger.info("Article title: " + self._article_title)
            self._logger.info("Artcicle keywords: " + self._article_seo_keywords)
            self._cache.write_cache_article(self._cache.tag_title(), self._article_title)
            self._cache.write_cache_article(self._cache.tag_seo_keywords(), self._article_seo_keywords)

    def _generate_chapters_title_and_description(self):

        if self._cache.is_article_chapters_list_cached() and self._cache.is_article_chapters_list_headers_cached():
            article_chapters_str = self._cache.get_cached_article_chapters_list()
            article_chapters_description_str = self._cache.get_cached_article_chapters_list_headers()
            self._article_chapters = article_chapters_str.split(', ')
            self._article_chapters_header = article_chapters_description_str.split(', ')
            self._logger.info("Article chapters [LOADED FROM CACHE]: " + article_chapters_str)
            self._logger.info("Article chapters headers [LOADED FROM CACHE]: " + article_chapters_description_str)
        else:
            self._article_chapters, self._article_chapters_header = self._editor.generate_article_chapters(self._article_title, self._article_seo_keywords)      
            chapters_list_str = ', '.join(self._article_chapters)
            chapters_description_list_str = ', '.join(self._article_chapters_header)
            self._logger.info("Article chapters: " + chapters_list_str)
            self._logger.info("Article chapters headers: " + chapters_description_list_str)
            self._cache.write_cache_article(self._cache.tag_chapters_list(), chapters_list_str)
            self._cache.write_cache_article(self._cache.tag_chapters_list_header(), chapters_description_list_str)
    
    def _generate_chapters(self):

        self._chapter_content = []
        last_chapter_content = " "
        for (index, _) in enumerate(self._article_chapters):

            if self._cache.is_article_chapters_content_cached()[index]:
                self._chapter_content.append(self._cache.get_cached_article_chapters_content()[index])
                self._logger.info("Chapter \"" + self._article_chapters[index] + "\" [LOADED FROM CACHE]")
            else:
                self._chapter_content.append(self._writer.generate_article_chapter(self._article_title, self._article_seo_keywords, 
                                                                            self._article_chapters, self._article_chapters_header, index,
                                                                            last_chapter_content))
                self._cache.write_cache_article(self._cache.tag_chapters_content(), self._chapter_content[index], self._article_chapters[index],)
                self._logger.info("Chapter \"" + self._article_chapters[index] + "\" generated successfully")

            last_chapter_content = self._chapter_content[index]
            self._logger.info(self._chapter_content[index])
            


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
        return self._article_text_consolidated

workers = {}
workers["editor"] = EditorGPT
workers["writer"] = WriterGPT

# Configure the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(level=logging.INFO)

# Configure the log format
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('blogself')

logger.info("Contacting OpenAI")

llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", openai_api_key=os.getenv("OPENAI_TEST_KEY"), temperature=0)
user_input_article_topic = "CAN Bus Demo on Arduino"

logger.info("Creating the blog article from topic: " + user_input_article_topic) 
blogself = BlogArticle(llm, user_input_article_topic, workers, logger)
print(blogself.get_overview())
print(blogself.get_article())
