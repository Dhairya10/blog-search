import json
import requests
import uuid
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
from scrapegraphai.graphs import SmartScraperGraph
from datetime import datetime
from config.settings import OPENAI_API_KEY
from config.logger import logger
from urllib.parse import urlparse
from typesense_search import TypesenseSearch


def get_blog_url(graph_config, input_file_name, output_file_name):
    # Read URLs from a text file
    with open(input_file_name, 'r') as file:
        urls_to_scrape = [line.strip() for line in file]

    all_blog_links = []

    for url in urls_to_scrape:
        smart_scraper_graph = SmartScraperGraph(
        prompt="List all the blog links on the website",
        source=url,
        config=graph_config
        )

        result = smart_scraper_graph.run()
        logger.info(f"Results for {url}:")
        logger.info(json.dumps(result, indent=2))

        if isinstance(result, dict) and 'blog_links' in result:
            all_blog_links.extend([f"{url}{link}" for link in result['blog_links']])
        else:
            logger.info(f"Unexpected result format for {url}")

    # Save all blog links to a txt file
    with open(output_file_name, 'w') as file:
        for link in all_blog_links:
            file.write(f"{link}\n")

    logger.info(f"All blog links have been saved to {output_file_name}")


def extract_date_from_html(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        date_p = soup.find('p', class_='txt--x-small txt--subtle align--center push_half--bottom')
        if date_p:
            return date_p.text.strip()
        
        return "Date not found"
    except Exception as e:
        logger.info(f"Error extracting date from {url}: {str(e)}")
        return "Date extraction failed"


def convert_to_iso(date_string):
    try:
        # Parse the date string
        date_obj = datetime.strptime(date_string, "%B %d, %Y")
        # Convert to ISO format
        return date_obj.isoformat()
    except ValueError:
        # If parsing fails, return the original string
        return date_string
    

def save_data(graph_config, input_file_name, output_file_name):
    # Read URLs from the file
    with open(input_file_name, 'r') as file:
        urls = [line.strip() for line in file]

    scraped_count = 0

    with open(output_file_name, 'w', encoding='utf-8') as jsonl_file:
        for url in tqdm(urls, desc="Scraping URLs"):
            try:
                smart_scraper_graph = SmartScraperGraph(
                    prompt="Extract the blog post title and content from this page and return the response with the following keys: title, content",
                    source=url,
                    config=graph_config
                )

                result = smart_scraper_graph.run()
                date = extract_date_from_html(url)
                date = convert_to_iso(date)

                # Extract author name from URL
                parsed_url = urlparse(url)
                author = parsed_url.path.split('/')[1] if len(parsed_url.path.split('/')) > 1 else 'Unknown'

                if isinstance(result, dict) and 'title' in result and 'content' in result:
                    scraped_data = {
                        'id': str(uuid.uuid4()),
                        'url': url,
                        'title': result.get('title', 'No title found'),
                        'content': result.get('content', 'No content found'),
                        'date': date,
                        'author': author
                    }
                else:
                    logger.info(f"Unexpected result format for {url}")
                    scraped_data = {
                        'id': str(uuid.uuid4()),
                        'url': url,
                        'title': 'Error: Unexpected result format',
                        'content': 'Error: Content not extracted',
                        'date': date,
                        'author': author
                    }

            except Exception as e:
                logger.info(f"Error scraping {url}: {str(e)}")
                scraped_data = {
                    'id': str(uuid.uuid4()),
                    'url': url,
                    'title': 'Error: Scraping failed',
                    'content': f'Error: {str(e)}',
                    'date': 'Error: Date not extracted',
                    'author': 'Unknown'
                }

            # Write the scraped data to the JSONL file
            json.dump(scraped_data, jsonl_file, ensure_ascii=False)
            jsonl_file.write('\n')

            scraped_count += 1

            # Add a delay to be respectful to the server
            time.sleep(1)

    logger.info(f"Scraped {scraped_count} articles. Content saved to {output_file_name}")


if __name__ == "__main__":
    graph_config = {
        "llm": {
            "api_key": OPENAI_API_KEY,
            "model": "gpt-3.5-turbo",
        },
    }
    input_file_name = "files/urls.txt"
    output_blog_file_name = "files/blog_links.txt"
    output_content_file_name = "files/content.jsonl"

    # Scrape and save to JSONL
    get_blog_url(graph_config, input_file_name, output_blog_file_name)
    save_data(graph_config, output_blog_file_name, output_content_file_name)

    # Add to Typesense
    typesense_search = TypesenseSearch()
    typesense_search.add_to_typesense(output_content_file_name)