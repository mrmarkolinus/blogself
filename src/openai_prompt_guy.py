import tiktoken
import data_analyst_guy
import openai

MAX_GPT4_TOKEN_LIMITS = 8192
MAX_GPT4_TOKEN_OUTPUT = 2000


def read_prompt_file(filename):
    # Open the file in binary mode
    with open(filename, 'rb') as file:
        # Read the content of the file
        content = file.read()
        
        # Try to decode the content using UTF-8 encoding
        try:
            decoded_string = content.decode('utf-8')
            #print(decoded_string)
        except UnicodeDecodeError as e:
            print(f"Error decoding file: {e}")
    return decoded_string

def get_google_queries_compact_gpt_format(data):
    gpt_compact_string = ""
    for row_id, inner_dict in data.items():
        list_values = list(inner_dict.values())
        gpt_compact_string += row_id + ":"
        for item in list_values[0].values:
            gpt_compact_string +=str(item[0]) + "," + str(item[1]) + ","
        gpt_compact_string = gpt_compact_string[:-1] + "-"
    gpt_compact_string = gpt_compact_string[:-1]
    return gpt_compact_string

def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-4")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def tokenize_information(source_websites_list):
    tokenized_prompt = ""
    content_tokens_total_count = 0
    for website in source_websites_list:
        website_content = data_analyst_guy.get_webpage_paragraph_text(website)
        content_tokens = num_tokens_from_string(":::" + website_content)
        if content_tokens_total_count + content_tokens > (MAX_GPT4_TOKEN_LIMITS - MAX_GPT4_TOKEN_OUTPUT):
            break
        content_tokens_total_count += content_tokens
        tokenized_prompt += ":::" + website_content
    return tokenized_prompt, content_tokens_total_count

def get_gpt_websites_summary(keyword_list, API_KEY, CSE_ID):

    prompt_guy_command = """you are an experienced data analyst. your goal is to summarize in as few words as possible the text i give you at the end of this prompt.
                        i may give you more textes separated by the format :::. For each text genearate a separate summary. Include the summary in the tags [S][/S]
                        important information that must be kept: data and statistics (graphs are important), insights, key information of the article. 
                        compact the output format as follow: [I]insights[\I][Q]quotes[\Q][G]stats for generating graphs[\G]. 
                        Your target is the openai API which accept only a limited amout of tokens. Here the textes: """

    source_websites_list = data_analyst_guy.search_updated_information_with_google(keyword_list, API_KEY, CSE_ID)
    tokenized_prompt, content_tokens_total_count = tokenize_information(source_websites_list)
    gpt_input_prompt = prompt_guy_command + tokenized_prompt

    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {
        "role": "user",
        "content": gpt_input_prompt
        }
    ],
    max_tokens=MAX_GPT4_TOKEN_OUTPUT
    )

    return response.choices[0]['message']['content']


def get_article_title_and_seo(gpt_format_trending_keywords):
    prompt_guy_command = """you are an experienced data analyst. your input is a set of data with the following format. the first word is the google search keyword. 
                            after the ":" couples of values with the format "keyword,value" define the popularity (or trend) of a certain topic. 
                            The popularity is sorted in descendant order. a '-' indicates the end of the list and the beginning of the next one with the same format. 
                            Analyze the data the best you can and think about 3 titles for a web blog which can go on top of the search engines. your target is the article writer. 
                            After thinking the 3 titles, please pick the one on which you could write the best blog article based on your knowledge cutoff. 
                            As output, give me only the title of the article and after a separator (::) the 5 most relevant input keywords you have considered to produce it. 
                            Your goal is to position at the top of the search engines and your target is a blog giving advices and updates.
                            Following are the data: """
    
    gpt_input_prompt = prompt_guy_command + gpt_format_trending_keywords

    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {
        "role": "user",
        "content": gpt_input_prompt
        }
    ],
    max_tokens=MAX_GPT4_TOKEN_OUTPUT
    )

    gpt_response_content = response.choices[0]['message']['content']

    # Split at '::' to get title and keywords string
    title, keywords_str = [part.strip() for part in gpt_response_content.split("::")]
    # Split keywords string at ',' to get a list of keywords and strip them
    #keywords = [keyword.strip() for keyword in keywords_str.split(",")]

    return title,keywords_str


def write_article_based_on_model_knowledge(article_tile, seo_keywords):

    prompt_guy_command_before_title = "You are a talented blog writer and SEO expert with thousands article written. you need to write an article with the title \""
    prompt_guy_command_after_title = "\". The article must be precise and detailed, but not boring. SEO is an extremely important parameter, relevant keywords are: "                                    
    prompt_guy_command_after_keywords = """. Your goal is to position at the top of the search engines and your target is a blog giving advices and updates. Think step by step.
                                        After having written the article, reread it and check if there are any errors, if so correct it and rewrite it again.
                                        The output of this prompt must be only the corrected article, then the separator ::: and then a comma separated list of the 5
                                        most relevant keywords i can search on google to go beyond your knowledge cutoff and update the article with updated data."""
    
    gpt_input_prompt = prompt_guy_command_before_title + article_tile + prompt_guy_command_after_title + seo_keywords + prompt_guy_command_after_keywords

    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {
        "role": "user",
        "content": gpt_input_prompt
        }
    ],
    max_tokens=MAX_GPT4_TOKEN_OUTPUT
    )

    gpt_response_content =  response.choices[0]['message']['content']

    # Split at '::' to get title and keywords string
    article_text, keywords_str = [part.strip() for part in gpt_response_content.split(":::")]
    # Split keywords string at ',' to get a list of keywords and strip them
    update_keywords = [keyword.strip() for keyword in keywords_str.split(",")]

    return article_text, update_keywords


def write_article_updated_with_internet_data(article_tile, article_text, seo_keywords, updated_information):

    prompt_guy_command_before_article = "You are a talented blog writer and SEO expert with thousands article written. You have written an article with the title: \""
    prompt_guy_command_after_title = "\". The content is the following and will end when you find ::: "
    prompt_guy_command_after_article =  """". Because of your knowledge cutoff, i have searched updated information on the internet for you. 
                                        You must integrate this information in your previous article. You may want to change the title of the article if necessary.
                                        These are the information and they will end when you find ::: """
    prompt_guy_command_after_info = "Do not ignore your previous article! Important: these are the SEO keywords you shall use, they will finish when you find ::: "                                     
    prompt_guy_command_after_keywords = """. Your goal is to position at the top of the search engines and your target is a blog giving advices and updates. 
                                        Whenever you find an interesting statistic or data, add the following format [GRAPH]Type-Xname-Yname-Xvalue-Yvalue[/GRAPH]
                                        Think step by step.
                                        After having written the article, reread it and check if there are any errors, if so correct it and rewrite it again.
                                        The output of this prompt must be only the fianl title followed by the final article"""
    
    gpt_input_prompt = prompt_guy_command_before_article + article_tile + prompt_guy_command_after_title + article_text + prompt_guy_command_after_article + updated_information + prompt_guy_command_after_info + seo_keywords + prompt_guy_command_after_keywords

    response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {
        "role": "user",
        "content": gpt_input_prompt
        }
    ],
    max_tokens=MAX_GPT4_TOKEN_OUTPUT
    )

    return response.choices[0]['message']['content']