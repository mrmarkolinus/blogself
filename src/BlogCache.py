import os
import re

STANDARD_STATUS_FILE_PATH = "src/.temp_gen/status.tmp"
STANDARD_ARTICLE_FILE_PATH = "src/.temp_gen/article.tmp"

CACHE_TAG_ARTICLE_TITLE = "TITLE"

class BlogCache():

    def __init__(self, load_at_init, status_file_path = STANDARD_STATUS_FILE_PATH, article_file_path = STANDARD_ARTICLE_FILE_PATH, pattern = r'###(\d+)###'):
        self._status_file_path = status_file_path
        self._article_file_path = article_file_path
        self._pattern = pattern

        self._cache_valid = False
        self._cached_status = ""
        self._cached_raw_content = ""
        self._cache_read_until = 0

        self._cached_title = ""
        self._cached_seo_keywords = ""
        self._cached_chapters_list = ""
        self._cached_chapters_list_headers = ""
        self._cached_chapters_content = ""
        self._cached_reviewed_content = ""

        self._cache_status_tags = {'IN_PROGRESS': 'PENDING',
                                   'FINISHED': 'DONE'
                                   }

        self._cache_content_tags = {'CACHE_TAG_ARTICLE_TITLE': 'TITLE', 
                                    'CACHE_TAG_ARTICLE_SEO_KEYWORDS': 'SEO_KEYWORDS', 
                                    'CACHE_TAG_ARTICLE_CHAPTERS_LIST': 'CHAPTERS_LIST',
                                    'CACHE_TAG_ARTICLE_CHAPTERS_LIST_HEADERS': 'CHAPTERS_LIST_HEADERS',
                                    'CACHE_TAG_ARTICLE_CHAPTERS_CONTENT': 'CHAPTERS_CONTENT',
                                    'CACHE_TAG_ARTICLE_REVIEWED_CONTENT': 'REVIEWED_CONTENT'
                        }

        if load_at_init:
            self._read_cache()

        if not self.is_valid():
            #start a new cache
            self._write_cache_status(self._cache_status_tags["IN_PROGRESS"])
        else:
            #recover content from cache
            self._recreate_blog_article()

    def is_valid(self):
        return self._cache_valid and self._cached_status != self._cache_status_tags["IN_PROGRESS"]
    
    def get_cached_article_title(self):
        if self.is_valid(): return self._cached_title
        else: return ""

    def get_cached_article_seo_keywords(self):
        if self.is_valid(): return self._cached_seo_keywords
        else: return ""
    
    def get_cached_article_chapters_list(self):
        if self.is_valid(): return self._cached_chapters_list
        else: return ""
    
    def get_cached_article_chapters_list_headers(self):
        if self.is_valid(): return self._cached_chapters_list_headers
        else: return ""
    
    def get_cached_article_chapters_content(self):
        if self.is_valid(): return self._cached_chapters_content
        else: return ""
    
    def get_cached_article_reviewed_content(self):
        if self.is_valid(): return self._cached_reviewed_content
        else: return ""
    
    def tag_title(self):
        return self._cache_content_tags["CACHE_TAG_ARTICLE_TITLE"]
    
    def tag_seo_keywords(self):
        return self._cache_content_tags["CACHE_TAG_ARTICLE_SEO_KEYWORDS"]
    
    def tag_chapters_list(self):
        return self._cache_content_tags["CACHE_TAG_ARTICLE_CHAPTERS_LIST"]
    
    def tag_chapters_list_header(self):
        return self._cache_content_tags["CACHE_TAG_ARTICLE_CHAPTERS_LIST_HEADERS"]
    
    def tag_chapters_content(self):
        return self._cache_content_tags["CACHE_TAG_ARTICLE_CHAPTERS_CONTENT"]
    
    def tag_reviewed_content(self):
        return self._cache_content_tags["CACHE_TAG_ARTICLE_REVIEWED_CONTENT"]

    def write_cache_article(self, article_step, article_content):
        with open(self._article_file_path, "a+") as file:
            file.write("[" + article_step + "]\n"+ article_content + "\n[/" + article_step +  "]\n\n")

    def _recreate_blog_article(self):

        is_cached, self._cached_title = self._recreate_from_cached_content("CACHE_TAG_ARTICLE_TITLE") 
        if not is_cached: return
        
        is_cached, self._cached_seo_keywords = self._recreate_from_cached_content("CACHE_TAG_ARTICLE_SEO_KEYWORDS")
        if not is_cached: return

        is_cached, self._cached_chapters_list = self._recreate_from_cached_content("CACHE_TAG_ARTICLE_CHAPTERS_LIST")
        if not is_cached: return

        is_cached, self._cached_chapters_list_headers = self._recreate_from_cached_content("CACHE_TAG_ARTICLE_CHAPTERS_LIST_HEADERS")
        if not is_cached: return

        is_cached, self._cached_chapters_content = self._recreate_from_cached_content("CACHE_TAG_ARTICLE_CHAPTERS_CONTENT")
        if not is_cached: return

        is_cached, self._cached_reviewed_content = self._recreate_from_cached_content("CACHE_TAG_ARTICLE_REVIEWED_CONTENT")
        if not is_cached: return

    def _recreate_from_cached_content(self, section_tag):
        unread_cache = self._cached_raw_content[self._cache_read_until:]
        match_found = False
        match_content = ""

        match_tag_open = re.search("[" + self._cache_content_tags[section_tag] + "]", unread_cache)
        match_tag_closed = re.search("[/" + self._cache_content_tags[section_tag] + "]", unread_cache)

        if match_tag_open and match_tag_closed:
            self._cache_read_until = match_tag_closed.end()
            match_content = self._cached_raw_content[match_tag_open.start():match_tag_closed.start()]
            match_found = True
        
        return match_found, match_content

    # # Find all occurrences of the pattern in the text
    # matches = re.finditer(self._pattern, cached_article)

    # # Initialize the variable to store the content
    # match_end = 0
    # for match in matches:
    #     chapter_content_list.append(cached_article[match_end:match.start()])
    #     match_end = match.end()


    def _write_cache_status(self, status):
        with open(self._status_file_path, "w") as file:
            file.write(status)

    def _read_cache(self):

        if os.path.exists(self._status_file_path) and os.path.exists(self._article_file_path):
            self._cache_valid = True
            
            with open(self._status_file_path, "r") as file:
                self._cached_status = file.read()

            with open(self._article_file_path, "r") as file:
                self._cached_raw_content = file.read()