import data_analyst_guy
import openai_prompt_guy
import openai
import os

#prova branch

# OPENAI API KEY, GOOGLE API KEY AND CSE ID
openai.api_key = os.getenv("OPENAI_TEST_KEY")
API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
CSE_ID = os.getenv("GOOGLE_CSE_ID")

#General artcile topic. These keyword (up to 5), will be used to search on google trends for top trend queries.
#kw_list = ["travel", "reise", "urlaub", "hotel", "airbnb"]

kw_list = ["minecraft", "mcc"]

#the data guy search for the queries
trending_related_queries = data_analyst_guy.get_latest_top_search_trend(kw_list)

#the prompt guy translate the results in gpt format (limited context up to 8k tokens)
gpt_format_trending_queries = openai_prompt_guy.get_google_queries_compact_gpt_format(trending_related_queries)

#the prompt guy asks gpt to decide a title for the article and ask for 5 SEO keywords
article_title, article_seo_keywords = openai_prompt_guy.get_article_title_and_seo(gpt_format_trending_queries)

#the prompt guy asks gpt to write an article, first based only on GPT knowledge before cutoff
article_text_based_on_model_knowledge, keywords_for_update = openai_prompt_guy.write_article_based_on_model_knowledge(article_title, article_seo_keywords)

#based on the model knowledge keywords, the data guy googles updated info on the topics suggested by gpt. It returns a list of websites to read for more information
url_lists = data_analyst_guy.search_updated_information_with_google(keywords_for_update, API_KEY, CSE_ID)

#because of the gpt limited context, the data guy will summarize the websites using gpt, passing the entire informationit to gpt again for the final article
summarized_uptodate_information = openai_prompt_guy.get_gpt_websites_summary(url_lists, API_KEY, CSE_ID)

final_article = openai_prompt_guy.write_article_updated_with_internet_data(article_title, article_text_based_on_model_knowledge, article_seo_keywords, summarized_uptodate_information)


print(article_title)
print("----")
print(article_seo_keywords)
print("----")
print(article_text_based_on_model_knowledge)
print("----")
print(keywords_for_update)
print("----")
print(url_lists)
print("----")
print(summarized_uptodate_information)
print("----")
print(final_article)

