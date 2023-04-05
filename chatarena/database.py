"""
Datastore module for chat_arena.
This module provides utilities for storing the messages and the game results into database.
Currently, it supports Supabase.
"""
import json
import os
from typing import List
import uuid

from .arena import Arena
from .message import Message

# Attempt importing Supabase
try:
    import supabase

    # Get the Supabase URL and secret key from environment variables
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY", "")
    assert SUPABASE_URL and SUPABASE_SECRET_KEY
except:
    supabase_available = False
else:
    supabase_available = True


# Store the messages into the Supabase database
class SupabaseDB:
    def __init__(self):
        assert supabase_available and SUPABASE_URL and SUPABASE_SECRET_KEY
        supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
        self.client = supabase_client

    # Save Arena state to Supabase
    def save_arena(self, arena: Arena):
        # Save the environment config
        self._save_environment(arena)

        # Save the player configs
        self._save_player_configs(arena)

        # Save the messages
        self.save_messages(arena)

    # Save the environment config of the arena
    def _save_environment(self, arena: Arena):
        env = arena.environment
        env_config = env.to_config()
        moderator_config = env_config.pop("moderator", None)

        arena_row = {
            "arena_id": str(arena.uuid),
            "global_prompt": arena.global_prompt,
            "env_type": env_config["env_type"],
            "env_config": json.dumps(env_config),
        }
        self.client.table("Arena").insert(arena_row).execute()

        # Get the moderator config
        if moderator_config:
            moderator_row = {
                "moderator_id": str(uuid.uuid5(arena.uuid, json.dumps(moderator_config))),
                "arena_id": str(arena.uuid),
                "role_desc": moderator_config["role_desc"],
                "terminal_condition": moderator_config["terminal_condition"],
                "backend_type": moderator_config["backend"]["backend_type"],
                "temperature": moderator_config["backend"]["temperature"],
                "max_tokens": moderator_config["backend"]["max_tokens"],
            }
            self.client.table("Moderator").insert(moderator_row).execute()

    # Save the player configs of the arena
    def _save_player_configs(self, arena: Arena):
        player_rows = []
        for player in arena.players:
            player_config = player.to_config()
            player_row = {
                "player_id": str(uuid.uuid5(arena.uuid, json.dumps(player_config))),
                "arena_id": str(arena.uuid),
                "name": player.name,
                "role_desc": player_config["role_desc"],
                "backend_type": player_config["backend"]["backend_type"],
                "temperature": player_config["backend"].get("temperature", None),
                "max_tokens": player_config["backend"].get("max_tokens", None),
            }
            player_rows.append(player_row)

        self.client.table("Player").insert(player_rows).execute()

    # Save the messages
    def save_messages(self, arena: Arena, messages: List[Message] = None):
        if messages is None:
            messages = arena.environment.get_observation()

        # Filter messages that are already logged
        messages = [msg for msg in messages if not msg.logged]

        message_rows = []
        for message in messages:
            message_row = {
                "message_id": str(uuid.uuid5(arena.uuid, message.msg_hash)),
                "arena_id": str(arena.uuid),
                "agent_name": message.agent_name,
                "content": message.content,
                "turn": message.turn,
                "timestamp": str(message.timestamp),
                "msg_type": message.msg_type,
                "visible_to": json.dumps(message.visible_to),
            }
            message_rows.append(message_row)

        self.client.table("Message").insert(message_rows).execute()

        # Mark the messages as logged
        for message in messages:
            message.logged = True


# Log the arena results into the Supabase database
def log_arena(arena: Arena, database=None):
    if database is None:
        pass
    else:
        database.save_arena(arena)


# Log the messages into the Supabase database
def log_messages(arena: Arena, messages: List[Message], database=None):
    if database is None:
        pass
    else:
        database.save_messages(arena, messages)
