import ssl
import certifi
import os
import json
from datetime import datetime, timedelta

from slack_sdk import WebClient
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = 'CAK6KLTCY'  # #general
PLAYER_MAP_FILE = os.path.join(os.path.dirname(__file__), 'slack_player_map.json')

def get_client():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    token = os.getenv('SLACK_BOT_TOKEN')
    if not token:
        print("Error: SLACK_BOT_TOKEN not set. Check your .env file.")
        return None
    return WebClient(token=token, ssl=ssl_context)

def load_player_map():
    with open(PLAYER_MAP_FILE) as f:
        return json.load(f)

def save_player_map(player_map):
    with open(PLAYER_MAP_FILE, 'w') as f:
        json.dump(player_map, f, indent=4)

def resolve_user_name(client, user_id):
    """Get a display name for a Slack user ID using the profile API."""
    resp = client.api_call('users.profile.get', params={'user': user_id})
    profile = resp['profile']
    return profile.get('display_name') or profile.get('real_name') or user_id

def find_weekly_post(client, look_back_days=7):
    """
    Find the most recent Wednesday reminder post in #general.
    Looks for messages containing thumbsup/thumbsdown reaction prompts.
    """
    oldest = datetime.now() - timedelta(days=look_back_days)
    oldest_ts = str(oldest.timestamp())

    resp = client.conversations_history(
        channel=CHANNEL_ID,
        oldest=oldest_ts,
        limit=50
    )

    for msg in resp['messages']:
        # Look for the weekly post - it asks for +1 / -1 reactions
        text = msg.get('text', '').lower()
        reactions = msg.get('reactions', [])
        has_thumbsup = any(r['name'] == '+1' for r in reactions)

        if has_thumbsup and ('reaction' in text or ':+1:' in text or ':-1:' in text):
            return msg

    return None

def get_attendees_from_post(client, message):
    """Get player names from thumbsup reactions on a message."""
    player_map = load_player_map()
    reactions = message.get('reactions', [])

    thumbsup_users = []
    guest_reactions = {}  # user_id -> number of guests
    for reaction in reactions:
        if reaction['name'] == '+1':
            thumbsup_users = reaction['users']
        elif reaction['name'] == 'one':
            for uid in reaction['users']:
                guest_reactions[uid] = 1
        elif reaction['name'] == 'two':
            for uid in reaction['users']:
                guest_reactions[uid] = 2

    attendees = []
    unmapped = []
    for user_id in thumbsup_users:
        if user_id in player_map:
            attendees.append(player_map[user_id])
        else:
            slack_name = resolve_user_name(client, user_id)
            unmapped.append((user_id, slack_name))

    # Resolve guest-bringing users to (name, count) tuples
    bringing_guests = []
    for user_id, count in guest_reactions.items():
        if user_id in player_map:
            bringing_guests.append((player_map[user_id], count))
        else:
            slack_name = resolve_user_name(client, user_id)
            bringing_guests.append((slack_name, count))

    return attendees, unmapped, bringing_guests

def get_weekly_attendees():
    """Main function: find this week's post and return who's coming."""
    client = get_client()
    if not client:
        return None, None, None

    post = find_weekly_post(client)
    if not post:
        print("Could not find this week's Wednesday post in #general")
        return None, None, None

    attendees, unmapped, bringing_guests = get_attendees_from_post(client, post)

    if unmapped:
        print("Unmapped Slack users (add them to slack_player_map.json):")
        for user_id, slack_name in unmapped:
            print(f"  {user_id}: \"{slack_name}\"")
        print()

    return attendees, unmapped, bringing_guests
