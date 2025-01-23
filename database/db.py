import sys
import mongoengine
from mongoengine import (Document, StringField, ListField, IntField, BooleanField, DictField,
                         DateTimeField)
from config import load_config


cfg, _ = load_config(sys.argv[1])

host = cfg.database.host
port = cfg.database.port
db = cfg.database.db
user = cfg.database.user
pwd = cfg.database.pwd

# mongoengine.connect("local")
mongoengine.connect(db, host=host, port=port, username=user, password=pwd)


class Guild(Document):
    meta = {"collection": "guilds"}
    guild_id = StringField(required=True, unique=True, max_length=128)
    name = StringField(required=True, max_length=256)
    data = DictField(default={})


class User(Document):
    meta = {"collection": "users"}

    display_name = StringField()
    username = StringField()
    discord = StringField()

    data = DictField(default={})
    options = DictField(default={})
    permissions = DictField(default={})
    tags = ListField(default=[])

    def __init__(self, username, discord, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.display_name = username
        self.discord = discord


class Quote(Document):
    meta = {"collection": "quotes"}
    quotes = ListField(StringField())
    users = ListField(StringField())
    enabled = BooleanField(default=True)

    guild_id = StringField(required=True)
    channel_id = StringField(required=True)
    message_id = StringField(required=True)

    dt = DateTimeField(required=True)
    added_by = StringField(required=True)


class WordleGame(Document):
    meta = {"collection": "wordle"}
    user_id = StringField(required=True, max_length=128)
    msg_id = IntField(required=True, unique=True)
    game = IntField(required=True)
    score = IntField(required=True)
    hard_mode = BooleanField(required=True)
    msg_content = StringField(required=True, max_length=1024)
    guesses = ListField(StringField(max_length=50))


class CmdUse(Document):
    meta = {"collection": "stats"}
    user_id = StringField(required=True, max_length=128)
    message_id = StringField(required=True, unique=True, max_length=128)
    channel_id = StringField(required=True, max_length=128)
    guild_id = StringField(required=True, max_length=128)

    content = StringField(required=True, max_length=1024)
    dt = StringField(required=True, max_length=128)
