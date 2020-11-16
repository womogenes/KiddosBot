import discord
from discord.ext import commands
from discord.utils import get

import random
import sys
import os
import time
import json
from bson.objectid import ObjectId as oid
from datetime import datetime as dt
import requests
from pymongo import MongoClient
from pprint import pprint

from html import unescape
from tabulate import tabulate

class Client(discord.Client):
    
    from ._on_ready import on_ready
    from ._on_message import _on_message
    from ._send_quote import send_quote
    from ._trivia import replenish_cache, send_trivia, answer_trivia
    from ._leaderboard import clear_leaderboard, clean_leaderboard, update_leaderboard
    from ._other import teehee, ping, gpt2_chat
    from ._points import give_points, donate_points, balance, reward
    from ._inherited import fetch_user
    from ._reactions import react
    from ._help import send_help_text
    from ._meta import logout, commit
    from ._databasing import get_attrib
    from ._announcements import clean_announcements, clear_announcements
    
    def initialize(self):
        with open("./static/mongo-info.json") as fin:
            mongoInfo = json.load(fin)
            url = f"mongodb+srv://womogenes:{mongoInfo['password']}@cluster0.w4adg.mongodb.net/{mongoInfo['dbname']}?retryWrites=true&w=majority"
            self.db = MongoClient(url).main
            print("Established MongoDB connection!")
        
        self.lastSent = dt.strptime(next(self.db.dateInfo.find({}))["last-sent-quote"], "%Y-%m-%d %H:%M:%S.%f")
        
        # Reset weekly points on a ?day.
        if dt.now().weekday() == 0 and dt.strptime(next(self.db.dateInfo.find({}))["last-reset-weekly-points"], "%Y-%m-%d %H:%M:%S.%f").date() != dt.now().date():
            self.db.users.update_many({}, {"$set": {"weekly": 0}})
            self.db.dateInfo.update_one({}, {"$set": {"last-reset-weekly-points": str(dt.now())}})
            print("Weekly point reset finished.")
        
        
        self.prefix = "\\"
        self.helpEmbed = None
        
        self.questionCache = []
        
        self.question = None
        self.answers = None
        self.rightAnswer = None
        self.answered = True
        self.lastSentQuestion = 0
        self.lastUpdatedLeaderboard = 0
        
        self.botChannel = self.get_channel(762173542233407528)
        self.quoteChannel = self.get_channel(761340228450910250)
        self.leaderboardChannel = self.get_channel(763825477533302856)
        self.announcementsChannel = self.get_channel(774135689163440188)
        self.userCache = {}
        
        self.lbMessages = [767193706590765096, 767193709476446209, 767193712387293245]