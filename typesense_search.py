import typesense
from config.settings import OPENAI_API_KEY, TYPESENSE_NODE, TYPESENSE_API_KEY
from config.logger import logger

class TypesenseSearch:
    def __init__(self):
        self.client = typesense.Client({
            'nodes': [{
                'host': TYPESENSE_NODE,
                'port': '443',
                'protocol': 'https'
            }],
            'api_key': TYPESENSE_API_KEY,
            'connection_timeout_seconds': 300  # high timeout because of batch document upload
        })

    def add_to_typesense(self, output_file):
        schema = {
            "name": "blog_posts",
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "author", "type": "string"},
                {"name": "title", "type": "string"},
                {"name": "content", "type": "string"},
                {"name": "date", "type": "string"},
                {"name": "url", "type": "string"},
                {
                    "name": "title_embedding",
                    "type": "float[]",
                    "num_dim": 1536,
                    "embed": {
                        "from": ["title"],
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
                        "from": ["content"],
                        "model_config": {
                            "model_name": "openai/text-embedding-3-small",
                            "api_key": OPENAI_API_KEY
                        }
                    }
                }
            ],
        }

        # Create the Typesense collection
        self.client.collections.create(schema)

        # Add the documents to the collection
        with open(output_file) as jsonl_file:
            self.client.collections['blog_posts'].documents.import_(jsonl_file.read().encode('utf-8'), {'action': 'create'}, {'batch_size': 40})

        logger.info(f"Data added to Typesense")

    def search(self, query, author=None, limit=3):
        search_parameters = {
            'q': query,
            'query_by': 'title, content, content_embedding',
            'prefix': False,
            'limit': limit,
        }
        if author:
            search_parameters['filter_by'] = 'author:{}'.format(author)

        results = self.client.collections['blog_posts'].documents.search(search_parameters)
        
        parsed_results = []
        if 'hits' in results:
            for hit in results['hits']:
                document = hit['document']
                parsed_result = {
                    'id': document.get('id', 'N/A'),
                    'url': document.get('url', 'N/A'),
                    'title': document.get('title', 'No title'),
                    'author': document.get('author', 'Unknown')
                }
                parsed_results.append(parsed_result)
        else:
            logger.info("No results found.")    

        return parsed_results