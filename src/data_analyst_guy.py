import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import openai_prompt_guy

def get_text_length(text):
    words = text.split()
    word_count = len(words)
    return word_count 

def get_webpage_paragraph_text(url):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    try:
        # Fetch the webpage content
        response = requests.get(url, headers=hdr)
        response.raise_for_status()  # Raise an exception for HTTP errors
    
        # Parse the webpage using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
    
        # Extract text from all <p> tags
        paragraphs = soup.find_all('p')
        return ' '.join(para.get_text() for para in paragraphs)

    except requests.exceptions.HTTPError as err:
        print("ERROR: Website not accessible")
        return ""

def google_search(query, api_key, cse_id, **kwargs):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'q': query,
        'key': api_key,
        'cx': cse_id,
        **kwargs
    }
    response = requests.get(url, params=params)
    return response.json()

def search_updated_information_with_google(keyword_list, API_KEY, CSE_ID):
    link_list = []
    for keyword in keyword_list:
        result = google_search(keyword, API_KEY, CSE_ID)
        for item in result.get("items", []):
            #print(item.get("title"))
            link_list.append(item.get("link"))
    return link_list

def get_latest_top_search_trend(kw_list):
    pytrends = TrendReq(hl='de', tz=60)
    pytrends.build_payload(kw_list, cat=0,timeframe='today 5-y', geo='DE', gprop='news')
    trends_related_queries = pytrends.related_queries()

    return trends_related_queries
    #return openai_prompt_guy.get_compact_gpt_format(trends_related_queries)