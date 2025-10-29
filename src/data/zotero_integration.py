import os
from dotenv import load_dotenv
from pyzotero import zotero
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ZOTERO_USER_ID = os.getenv('ZOTERO_USER_ID')
ZOTERO_API_KEY = os.getenv('ZOTERO_API_KEY')

def get_zotero_client(group_id=None):
    """
    Initializes and returns a Zotero client object.
    If group_id is provided, it connects to a group library, otherwise to the user's personal library.
    """
    if not ZOTERO_USER_ID or not ZOTERO_API_KEY:
        logging.error("Zotero User ID or API Key not found in environment variables.")
        raise ValueError("Zotero User ID and API Key must be set in the .env file.")

    if group_id:
        logging.info(f"Connecting to Zotero group library with ID: {group_id}")
        return zotero.Zotero(group_id, 'group', ZOTERO_API_KEY)
    else:
        logging.info(f"Connecting to Zotero personal library with User ID: {ZOTERO_USER_ID}")
        return zotero.Zotero(ZOTERO_USER_ID, 'user', ZOTERO_API_KEY)

def get_articles_metadata(zot, collection_id=None, limit=100):
    """
    Fetches article metadata from Zotero.
    Optionally filters by collection.
    """
    try:
        if collection_id:
            logging.info(f"Fetching items from collection ID: {collection_id}")
            if limit < 100:
                items = zot.collection_items(collection_id, limit=limit)
            else:
                items = zot.everything(zot.collection_items_top(collection_id, limit=limit))
        else:
            logging.info("Fetching top-level items.")
            items = zot.top(limit=limit)

        articles_metadata = []
        for item in items:
                articles_metadata.append(item)
        logging.info(f"Found {len(articles_metadata)} articles metadata.")
        return articles_metadata
    except Exception as e:
        logging.error(f"Error fetching articles metadata from Zotero: {e}")
        return []

def pull_from_zotero(collection_id="SVUM4G2M"):
    zot = get_zotero_client()
    articles_metadata = get_articles_metadata(zot, collection_id=collection_id, limit=106)
    return articles_metadata

if __name__ == '__main__':
    # Example Usage:
    try:
        # Replace with your actual group_id if you want to access a group library
        # zot = get_zotero_client(group_id='YOUR_GROUP_ID')
        zot = get_zotero_client() # Connects to personal library

        # Replace with your actual collection_id if you want to fetch from a specific collection
        # articles_metadata = get_articles_metadata(zot, collection_id='YOUR_COLLECTION_ID', limit=5)
        articles_metadata = get_articles_metadata(zot, collection_id="SVUM4G2M", limit=106) # Fetch top 106 articles metadata from personal library

        if articles_metadata:
            print(f"Fetched {len(articles_metadata)} articles metadata:")
            #for article in articles_metadata:
                #print(f"- {article['data'].get('title', 'No Title')} (Key: {article['data']['key']})")
        else:
            print("No articles metadata found.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
