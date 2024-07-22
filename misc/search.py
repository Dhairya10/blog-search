import typesense
from config.settings import TYPESENSE_NODE, TYPESENSE_API_KEY
from config.logger import logger

client = typesense.Client({
  'nodes': [{
    'host': TYPESENSE_NODE,
    'port': '443',
    'protocol': 'https'
  }],
  'api_key': TYPESENSE_API_KEY,
  'connection_timeout_seconds': 300 # high timeout because of batch document upload
})

def search(query):
    search_parameters = {
        'q': query,
        'query_by': 'title, content, content_embedding',
        'prefix': False,
        'limit': 3
    }

    results = client.collections['blog_posts'].documents.search(search_parameters)
    
    parsed_results = []
    if 'hits' in results:
        for hit in results['hits']:
            document = hit['document']
            parsed_result = {
                'id': document.get('id', 'N/A'),
                'url': document.get('url', 'N/A'),
                'title': document.get('title', 'No title')
            }
            parsed_results.append(parsed_result)
    else:
        logger.info("No results found.")    

    return parsed_results