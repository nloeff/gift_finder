from collections import namedtuple
from typing import List
import requests
import argparse
import openai
import re
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from flask import Flask, request, render_template


# Listing named tuple
Listing = namedtuple('Listing', 'title href id pos src')

# Flask App
app = Flask(__name__)
app.config.from_object(__name__)

# Templates
PROMPT_TEMPLATE = '{num_ideas} good ideas for queries for gifts to find on Etsy for {query} are'
ETSY_QUERY_URL_TEMPLATE = 'https://www.etsy.com/search?q={query}'

# Defaults (to save query time)
DEFAULT_QUERY = 'a nephew who loves pokemon'
DEFAULT_RESPONSE = ['Pokemon Plush Toy', 'Pokemon Collectors Pin Badge Set',
    'Personalized Pokemon Birthday Card', 'Pokemon-Themed Art Print', 'Pokemon-Themed T-Shirt']

def gpt_query_generator(query: str, num_ideas: int) -> List[str]:
    """
    Generates lists of GPT-3 query suggestions based on prompt query
    Inputs:
        - query: String with query
        - num_ideas: How many query suggestions GPT-3 should generate
    Output:
        List of queries
    """
    prompt = PROMPT_TEMPLATE.format(num_ideas=num_ideas, query=query)
    gpt_response = openai.Completion.create(
        model='text-davinci-003',
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )    
    gpt_suggestions = gpt_response.choices[0].text.split('\n')[2:] # Beginning is always ': \n\n'
    gpt_queries = [re.sub('^[0-9]+\.\s', '', query.rstrip()) for query in gpt_suggestions] # Remove "row number" from suggestions
    return gpt_queries

# Transform query into Etsy URL
etsy_query_url = lambda query: ETSY_QUERY_URL_TEMPLATE.format(query=quote_plus(query))

def query_etsy(query: str, num_listings: int) -> List[Listing]:
    """
    Generates a list of (non-ads) Listings given a query on Etsy.com 
    Inputs:
        - query: String with suggested query
        - num_listings: number of listings to display per query
    Output:
        List of Listings for each query
    """    
    page = requests.get(etsy_query_url(query))
    soup = BeautifulSoup(page.content, 'html.parser')
    listings = []
    links = soup.select('a.listing-link.wt-display-inline-block')
    for anchor in links[:num_listings]:
        listing = Listing(
            anchor.get('title'),
            anchor.get('href'),
            anchor.get('data-listing-id'),
            anchor.get('data-position-num'),
            anchor.div.div.div.div.div.div.img.get('src'),
        )
        listings.append(listing)
        print(query, listing)
    return listings


@app.route('/')
def index() -> str:
    query = request.args.get('query', DEFAULT_QUERY)
    gpt_queries = DEFAULT_RESPONSE if query is DEFAULT_QUERY else gpt_query_generator(query, NUM_IDEAS)
    listings_per_query = [(query, etsy_query_url(query), query_etsy(query, NUM_RES)) for query in gpt_queries]
    title = 'Perfect Etsy results for {query}'.format(query=query)

    return render_template('index.html', 
            query=query,
            title=title, 
            listings_per_query=listings_per_query,
            num_results=NUM_IDEAS, 
            n_cols=NUM_RES)

def build_arg_parser():
    parser = argparse.ArgumentParser(
        description='An app to find the perfect gift at Etsy',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--api-key", 
            dest='api_key',
            type=str,
            required=True,
            help="Open AI API key (required to run GPT-3).")

    parser.add_argument("--host",
            dest="host",
            default="127.0.0.1",
            help="Host IP Address. Default is localhost (127.0.0.1)")

    parser.add_argument("--port",
            dest="port",
            default=8888,
            type=int,
            help="Host Port Address. Default is 8888")

    parser.add_argument("--num-results",
            dest="num_results",
            default=5,
            type=int,
            help="Number of results to render per query. Default is 5. Min is 1. Max is 6.")

    parser.add_argument("--num-ideas", 
            dest='num_ideas',
            type=int,
            default=5,
            help="Number of rows/ideas to visualize. Default is 5. Max is 10.")

    return parser

if __name__ == '__main__':
    args = build_arg_parser().parse_args()
    openai.api_key = args.api_key
    assert(args.num_ideas >= 0 and args.num_ideas <= 10, 'num-ideas must be an integer and  and 0 <= num-ideas <= 10')
    NUM_IDEAS = args.num_ideas
    assert(args.num_results >=0 and args.num_results <=6 , 'num-results must be an integer and 0 <= num-results <= 6')
    NUM_RES = args.num_results
    app.run(host=args.host, port=args.port)