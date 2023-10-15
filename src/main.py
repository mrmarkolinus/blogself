from langchain.chat_models import ChatOpenAI
from editors import EditorGPT
from writers import WriterGPT
from BlogCache import BlogCache
from BlogArticle import BlogArticle
import os
import logging
import html
import re


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
blogself = BlogArticle(llm, user_input_article_topic, workers, logger, generate_at_init=True)
#print(blogself.get_overview())
#print(blogself.get_article())
#blogself.get_article_from_file()
blogself.to_html()
article_html_pre_text = """<!DOCTYPE html>
                            <html lang="en">

                            <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>Blog Article</title>
                                <link rel="stylesheet" href="styles.css">
                            </head>

                            <body>

                                <header>
                                    <h1>My Blog</h1>
                                </header>

                                <main>
                                    <article>
                                        <h2 class="article-title">Article Title Here</h2>
                                        <div class="article-meta">
                                            <span>Published on: <time datetime="2023-10-15">October 15, 2023</time></span>
                                            <span>Author: John Doe</span>
                                        </div>
                                        <div class="article-content">
                        """
article_html_post_text = """</div>
                                </article>
                            </main>

                            <footer>
                                <p>&copy; 2023 My Blog. All rights reserved.</p>
                            </footer>

                        </body>

                        </html>


                        """


blog_html_page = article_html_pre_text + blogself.to_html() + article_html_post_text

with open("./src/output/test/article.html", "w+") as f:
    f.write(blog_html_page)