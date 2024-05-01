"""Module providing access to the valling restful endpoints."""
import logging
from datetime import datetime
import random
from operator import itemgetter
import time
import requests
from flask import Flask, jsonify, request

random.seed(time.time())

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RESPONSE_LIMIT = 25

def filter_comments_by_time(comments, start_time, end_time):
    """method to filter the given set of comments based on the created by time value"""
    try:
        filtered_comments = [comment for comment in comments if end_time >= comment["created_at"] >= start_time]
        return filtered_comments
    except ValueError:
        # Handle invalid timestamp format
        return []
    except Exception as e:
        print(e)
        # Handle other exceptions
        return []

def find_sentiment_bulk(texts):
    """Dummy Function that will randomly assign a probability value to the comment
        and if the value is more than 0.5 it will mark it as positive else as negative"""
    try:
        response = []
        for comment in texts:
            ps = random.random()
            if ps > 0.5:
                sentiment = "positive"
            else:
                sentiment = "negative"
            semi_response = {
                "created_at":comment["created_at"],
                "id":comment["id"],
                "text": comment["text"],
                "polarity_score": ps,
                "sentiment": sentiment
            }
            response.append(semi_response)
        return response
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return [{'error': 'An unexpected error occurred'}], 500

def get_subfeddit_id_by_username(username):
    """ Function that will get the subfeddit if based on the username else return None"""
    try:
        base_url = "http://localhost:8080/api/v1/subfeddits/"
        limit = 10
        skip = 0
        while True:
            url = f"{base_url}?skip={skip}&limit={limit}"
            response = requests.get(url, timeout=20)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            data = response.json()
            # Iterate over the subfeddits and find the matching username
            for subfeddit in data.get('subfeddits', []):
                if subfeddit['username'] == username:
                    return subfeddit['id']
            # If the number of retrieved subfeddits is less than the limit, stop iterating
            if len(data.get('subfeddits', [])) < limit:
                break
            # Increment the skip value for pagination
            skip += limit
        # If no matching username is found
        return None
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch subfeddits: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_total_comments(subfeddit_id, skip=0, limit=33730):
    """ Function that will get the subfeddit total comments based on the id  else return []"""
    try:
        base_url= "http://localhost:8080/api/v1/comments"
        url = f"{base_url}/?subfeddit_id={subfeddit_id}&skip={skip}&limit={limit}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        data = response.json()
        comments = data.get('comments', [])
        if len(comments)> 0:
            comments = sorted(comments, key=lambda x: x['created_at'], reverse=True)
        return comments
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch comments: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

# Endpoint to fetch comments from a subreddit with optional time range filtering
@app.route('/subreddit/<subreddit_name>/comments', methods=['GET'])
def get_subreddit_comments(subreddit_name):
    """ Rest endpoint that will return A list of the most recent comments()
        RESPONSE_LIMIT variables sets the limit 
        Filter comments by a specific time range
        Sort the results by the comments polarity score."""
    try:
        subfeddit_id = get_subfeddit_id_by_username(subreddit_name)
        if subfeddit_id is None:
            return jsonify({"status":"failure","message":"unable to find the subreddit name"})
        comments = get_total_comments(subfeddit_id)
        comments_under_process = comments[0:RESPONSE_LIMIT]
        processed_comments = find_sentiment_bulk(comments_under_process)
        # Extract start_time and end_time from query parameters
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        descending = request.args.get('descending')
        if start_time_str is not None and end_time_str is not None:
            timestamp_start = datetime.fromisoformat(start_time_str.replace("Z", "+00:00")) 
            timestamp_start = int(timestamp_start.timestamp())
            timestamp_end = datetime.fromisoformat(end_time_str.replace("Z", "+00:00")) 
            timestamp_end = int(timestamp_end.timestamp())
            processed_comments = filter_comments_by_time(processed_comments,
                                                          timestamp_start,
                                                            timestamp_end)
        if descending is not None:
            if descending.lower() == "true":
                processed_comments = sorted(processed_comments,
                                             key=itemgetter("polarity_score"),
                                               reverse=True)
            else:
                processed_comments = sorted(processed_comments,
                                             key=itemgetter("polarity_score"),
                                               reverse=False)
        return jsonify(processed_comments), 200

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch comments from Feddit API: {e}")
        return jsonify({'error': 'Failed to fetch comments from Feddit API'}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


if __name__ == '__main__':
    app.run(debug=True)
