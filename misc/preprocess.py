import xml.etree.ElementTree as ET
import json
import html
import uuid
import typesense
from bs4 import BeautifulSoup
from config.logger import logger
from config.settings import OPENAI_API_KEY, TYPESENSE_NODE, TYPESENSE_API_KEY

author_feeds = {
    "Jason Fried": "files/feed_jason.atom",
    "DHH": "files/feed_dhh.atom"
}

def parse_rss_to_jsonl(author_name, input_file, output_file):
    # Parse the XML file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Define the namespace
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}

    # Open the output file in append mode
    with open(output_file, 'a', encoding='utf-8') as f:
        for entry in root.findall('atom:entry', namespace):
            random_id = str(uuid.uuid4())
            title = entry.find('atom:title', namespace).text
            content = entry.find('atom:content', namespace).text
            content = html.unescape(content)
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text(separator=' ', strip=True)
            date = entry.find('atom:published', namespace).textL
            url = entry.find('atom:link', namespace).get('href')

            # Create a dictionary with the extracted information
            data = {
                'id': random_id,
                'author': author_name,
                'title': title,
                'content': content,
                'date': date,
                'url': url
            }

            # Write the dictionary as a JSON line to the output file
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')

    logger.info(f"Parsing complete for {author_name}. Data appended to {output_file}")


def add_to_typesense(output_file):
  
    client = typesense.Client({
    'nodes': [{
        'host': TYPESENSE_NODE,
        'port': '443',
        'protocol': 'https'
    }],
    'api_key': TYPESENSE_API_KEY,
    'connection_timeout_seconds': 300 # high timeout because of batch document upload
    })

    schema = {
        "name": "blog_posts",
        "fields": [
      {
        "name": "id",
        "type": "string"
      },
      {
        "name": "author",
        "type": "string"
      },
      {
        "name": "title",
        "type": "string"
      },
      {
        "name": "content",
        "type": "string"
      },
      {
        "name": "date",
        "type": "string"
      },
      {
        "name": "url",
        "type": "string"
      },
      {
        "name": "title_embedding",
        "type": "float[]",
        "num_dim": 1536,
        "embed": {
          "from": [
            "title"
          ],
          "model_config": {
            "model_name": "openai/text-embedding-3-small",
            "api_key": OPENAI_API_KEY
          }
        }
      },
      {
        "name": "content_embedding",
        "type": "float[]",
        "num_dim": 1536,
        "embed": {
          "from": [
            "content"
          ],
          "model_config": {
            "model_name": "openai/text-embedding-3-small",
            "api_key": OPENAI_API_KEY
          }
        }
      }
    ],
  }

    # Create the Typesene collection
    client.collections.create(schema)

    # Add the documents to the collection
    with open(output_file) as jsonl_file:
        client.collections['blog_posts'].documents.import_(jsonl_file.read().encode('utf-8'), {'action': 'create'}, {'batch_size': 40})

    logger.info(f"Data added to Typesense")


if __name__ == "__main__":
    output_file = "files/output.jsonl"
    
    # Clear the output file if it exists
    open(output_file, 'w').close()

    for author, feed_file in author_feeds.items():
        parse_rss_to_jsonl(author, feed_file, output_file)

    logger.info(f"All parsing complete. Output written to {output_file}")

    add_to_typesense(output_file)