from apify_client import ApifyClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_apify_client():
    token = getattr(settings, 'APIFY_API_TOKEN', None)
    if not token or token == "YOUR_APIFY_API_TOKEN":
        logger.warning("Apify API Token is missing or not set.")
        return None
    return ApifyClient(token)

def run_actor(actor_id, run_input):
    client = get_apify_client()
    if not client:
        print(f"[APIFY DEBUG] Client creation failed - API token missing or invalid")
        return []

    try:
        print(f"[APIFY DEBUG] Starting actor: {actor_id}")
        print(f"[APIFY DEBUG] Input: {run_input}")
        
        # Start the actor and wait for it to finish
        run = client.actor(actor_id).call(run_input=run_input)
        print(f"[APIFY DEBUG] Actor run completed. Run ID: {run.get('id')}")
        
        # Fetch results from the default dataset
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
        print(f"[APIFY DEBUG] Retrieved {len(dataset_items)} items from dataset")
        
        if dataset_items:
            print(f"[APIFY DEBUG] First item sample: {dataset_items[0]}")
        
        return dataset_items
        
    except Exception as e:
        logger.error(f"Apify Actor Run Failed: {e}")
        print(f"[APIFY DEBUG] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_facebook_comments_apify(post_url):
    """
    Scrape Facebook comments using Apify Actor.
    Actor: apify/facebook-comments-scraper
    """
    actor_id = getattr(settings, 'APIFY_FACEBOOK_COMMENTS_ACTOR', "apify/facebook-comments-scraper")
    
    # Input format for Facebook comments scraper
    # startUrls must be array of objects with 'url' property
    run_input = {
        "startUrls": [{"url": post_url}],  # MUST be object with 'url' key
        "maxComments": 100,
        "commentsMode": "RANKED_UNFILTERED"
    }
    
    print(f"[APIFY DEBUG] Fetching Facebook comments for URL: {post_url}")
    data = run_actor(actor_id, run_input)
    
    # Extract names from the dataset items
    # The actor returns items with 'ownerName' or 'name' field
    names = []
    for item in data:
        # Try different possible field names
        name = (item.get("ownerName") or 
                item.get("profileName") or 
                item.get("name") or 
                item.get("owner", {}).get("name") or 
                item.get("user", {}).get("name"))
        
        if name and name != "Unknown User":
            names.append(name)
    
    print(f"[APIFY DEBUG] Extracted {len(names)} comment names: {names[:5]}")
    return names

def get_facebook_likes_apify(post_url):
    """
    Scrape Facebook post reactions using Apify Actor.
    Actor: alexey/facebook-likes-scraper (or similar dedicated scraper)
    """
    # Use a dedicated likes scraper instead of page scraper
    actor_id = getattr(settings, 'APIFY_FACEBOOK_LIKES_ACTOR', "alexey/facebook-likes-scraper")
    
    run_input = {
        "startUrls": [{"url": post_url}],
        "maxReactions": 100,  # Limit to control costs/time
        "proxy": {"useApifyProxy": True} # Often required
    }
    
    print(f"[APIFY DEBUG] Fetching Facebook likes for URL: {post_url} using {actor_id}")
    data = run_actor(actor_id, run_input)
    
    names = []
    # Dedicated likes scraper usually returns a list of reaction objects directly
    for item in data:
        # Check for name field directly
        name = (item.get("name") or 
                item.get("profileName") or 
                item.get("user", {}).get("name") or
                item.get("title")) # Sometimes title is the name
        
        if name and name != "Unknown User":
            names.append(name)
            
    # Fallback: If 'data' was a single object with 'reactions' field (old behavior)
    if not names and data and isinstance(data, list) and "reactions" in data[0]:
         print("[APIFY DEBUG] Detected nested reactions structure via fallback")
         for item in data:
            reactions = item.get("reactions") or []
            for reaction in reactions:
                 name = reaction.get("name")
                 if name: names.append(name)

    print(f"[APIFY DEBUG] Extracted {len(names)} like names: {names[:5]}")
    return names