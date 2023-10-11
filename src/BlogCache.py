import os
import re

STANDARD_STATUS_FILE_PATH = "src/.temp_gen/status.tmp"
STANDARD_ARTICLE_FILE_PATH = "src/.temp_gen/article.tmp"

class BlogCache():

    def __init__(self, status_file_path = STANDARD_STATUS_FILE_PATH, article_file_path = STANDARD_ARTICLE_FILE_PATH, pattern = r'###(\d+)###'):
        self._status_file_path = status_file_path
        self._article_file_path = article_file_path
        self._pattern = pattern
    
    def load_cached_content(self):
        cache_exists, cached_status, cached_article = self._read_cache_content()

        if cached_status == "finished":
            content_before_last_match = ""
        else:
            if not cache_exists:
                content_before_last_match = ""
            else:
                # Find all occurrences of the pattern in the text
                matches = re.finditer(self._pattern, cached_article)

                # Initialize the variable to store the content
                chapter_content_list = []
                match_end = 0
                for match in matches:
                    chapter_content_list.append(cached_article[match_end:match.start()])
                    match_end = match.end()

        return cache_exists, cached_status, chapter_content_list

    def write_cache_article(self, article_step, article_content):
        with open(self._article_file_path, "w") as file:
            file.write("###"+ article_step + "###")
            file.write("###"+ article_content + "###")
    
    def write_cache_status(self, status):
        with open(self._status_file_path, "w") as file:
            file.write(status)

    def _read_cache_content(self):

        if os.path.exists(self._status_file_path):
            cache_exists = True
            with open(self._status_file_path, "r") as file:
                cached_status = file.read()

            if os.path.exists(self._article_file_path):
                with open(self._article_file_path, "r") as file:
                    cached_article = file.read()
            else:
                cached_article = ""
                cache_exists = False
        else:
            cached_article = ""
            cached_status = ""
            cache_exists = False

        return cache_exists, cached_status, cached_article