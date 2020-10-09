# This example requires the 'members' privileged intents

import discord
from discord.ext import commands
from discord.utils import get

import random
import sys
import os
import time
import json
from datetime import datetime as dt
import requests
from pprint import pprint

from html import unescape

loadChatbot = False
if loadChatbot:
    sys.path.append(os.getcwd() + "/gpt2-chatbot")
    from chatbot import *
    chatbot = Bot()

import discord

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
shorten = lambda x: x if len(x) < 16 else x[:13] + "..."

class MyClient(discord.Client):
    
    def initialize(self):        
        with open("./data/date-info.json") as fin:
            quoteInfo = json.load(fin)
            self.lastSent = dt.strptime(quoteInfo["last-visited"], "%Y-%m-%d %H:%M:%S.%f")
            fin.close()
            
        with open("./data/trivia-info.json") as fin:
            self.triviaInfo = json.load(fin)
            fin.close()
            
        with open("./data/point-info.json") as fin:
            x = json.load(fin)
            self.points = {"lifetime": {}, "weekly": {}}
            for i in x["lifetime"]:
                self.points["lifetime"][int(i)] = x["lifetime"][i]
            for i in x["weekly"]:
                self.points["weekly"][int(i)] = x["weekly"][i]
            fin.close()
        
        # Reset weekly points on a Monday.
        if dt.now().weekday() == 4:
            maxWeekly = 0
            for i in self.points["weekly"]:
                maxWeekly = max(maxWeekly, self.points["weekly"][i])
                
            if maxWeekly != 0:
                for i in self.points["weekly"]:
                    self.points["weekly"][i] = 0
                with open("./data/point-info.json", "w") as fout:
                    json.dump(self.points, fout, indent=2)
            
        self.question = None
        self.answers = None
        self.rightAnswer = None
        self.answered = True
        
        self.botChannel = self.get_channel(762173542233407528)
        self.quoteChannel = self.get_channel(761340228450910250)
        self.leaderboardChannel = self.get_channel(763825477533302856)
        
        
    async def on_ready(self):
        """
        This function is called when the client is ready.
        """
        print("Logged on as " + str(self.user) + "!")
        self.initialize()
        await self.send_quote()
        
        
    async def send_quote(self):
        if self.lastSent.date() != dt.now().date():
            url = 'https://quotes.rest/qod?category=inspire'
            api_token = "X-TheySaidSo-Api-Secret"
            headers = {
                "content-type": "application/json",
                "X-TheySaidSo-Api-Secret": format(api_token)
            }

            response = requests.get(url, headers=headers)
            quotes = response.json()["contents"]["quotes"][0]
            
            # Spammy quotes!
            msgId = await self.quoteChannel.send(f"""**Quote of the day:**\n\n> {quotes["quote"]}\n\n~ *{quotes["author"]}*""")

            self.lastSent = dt.now()
            with open("./data/date-info.json", "w") as fout:
                json.dump({ "last-visited": str(self.lastSent) }, fout, indent=2)
                fout.close()
                
    
    async def send_trivia(self):
        url = "https://opentdb.com/api.php?amount=1"
        response = requests.get(url)
        
        if self.question == None or self.answered:
            self.question = f"**Trivia Question:**\n{unescape(response.json()['results'][0]['question'])}"
            self.rightAnswer = unescape(response.json()["results"][0]["correct_answer"]).strip()
            self.answers = [unescape(i).strip() for i in response.json()["results"][0]["incorrect_answers"] + [self.rightAnswer]]
            allNumeric = True
            for i in self.answers:
                allNumeric = allNumeric and i.isnumeric()
            if allNumeric:
                self.answers = [str(i) for i in sorted([int(j) for j in self.answers])]
            if len(self.answers) != 2 and not allNumeric:
                random.shuffle(self.answers)
            if len(self.answers) == 2:
                self.answers = ["True", "False"]
            self.answered = False
        
            # bot channel.
            text = self.question + "\n"
            for i in range(len(self.answers)):
                text += f"**{i + 1}**. {unescape(self.answers[i])}\n"
            await self.botChannel.send(text)
            
        elif not self.answered:
            await self.botChannel.send(self.question)
            
        else:
            await self.botChannel.send("There is currently no active question.\nUse `-t` for a new trivia question.")
        
        
    async def answer_trivia(self, message):
        if self.answered:
            #await self.botChannel.send("There is currently no active question.\nUse `-t` for a new trivia question.")
            return
            
        if len(message.content) < 4:
            return
        
        answer = message.content[3:]
        if answer.isdigit() and 1 <= int(answer) <= len(self.answers):
            correct = self.answers[int(answer) - 1] == self.rightAnswer
        else:
            return
            
        self.answered = True
        
        if message.author.id not in self.points["lifetime"]:
            self.points["lifetime"][message.author.id] = 0
            self.points["weekly"][message.author.id] = 0
        
        if correct:
            self.points["lifetime"][message.author.id] += 3
            self.points["weekly"][message.author.id] += 3
            await self.botChannel.send(f"""Correct! 🙂 {message.author.display_name} now has **{self.points["lifetime"][message.author.id]}** points.""")
            
        else:
            self.points["lifetime"][message.author.id] -= 1
            self.points["weekly"][message.author.id] -= 1
            await self.botChannel.send(f"""Sorry, {message.author.display_name} ☹ The right answer was **{self.rightAnswer}**.
{message.author.display_name} now has **{self.points["lifetime"][message.author.id]}** points.""")
        
        with open("./data/point-info.json", "w") as fout:
            json.dump(self.points, fout, indent=2)
            fout.close()
        
        await self.update_leaderboard()
    
    
    async def clean_leaderboard(self, message):
        if message.channel.id == 763825477533302856:
            if message.id != 763825813182611477:
                await message.delete()
                
                
    async def update_leaderboard(self):
        message = await self.leaderboardChannel.fetch_message(763825813182611477)
        text = "```Rank |" + " Name".ljust(18) + "| Points | This week\n"
        horiz = "-"
        text += horiz * 5 + "+" + horiz * 18 + "+" + horiz * 8 + "+" + horiz * 16 + "\n"
        s = sorted(self.points["weekly"].keys(), key=lambda x: (self.points["weekly"][x], self.points["lifetime"][x]), reverse=True)
        
        for i in range(len(self.points["lifetime"])):
            user = await self.fetch_user(s[i])
            if i == 0:
                namePart = " " + shorten(user.display_name).ljust(17)
            else:
                namePart = " " + shorten(user.display_name).ljust(17)
            text += f"{ordinal(i + 1).ljust(5)}|{namePart}| {str(self.points['lifetime'][s[i]]).ljust(7)}| {self.points['weekly'][s[i]]}\n"
        text += "```"
        await message.edit(content=text)
        

    async def on_message(self, message):
        clippedMessage = message.content if len(message.content) < 64 else message.content[:64]
        print(str(message.author).ljust(32) + "> " + clippedMessage + " " + str(dt.now()))
        
        channel = message.channel
        text = message.content
        
        if message.author == self.user:
            return
            
        # Do commands!
        if text.lower().strip() == "-t":
            await self.send_trivia()
            return
            
        if channel.id == 762173542233407528 and text.lower().startswith("-a"):
            await self.answer_trivia(message)
            return

        await self.clean_leaderboard(message)
        if await self.teehee(message): return
        if await self.ping(message): return
        if await self.gpt2_chat(message): return
        
    
    async def teehee(self, message):
        # This is Minoo.
        if message.author.id == 722965611012948018 and message.channel != self.botChannel:
            if random.randrange(5) < 1:
                await message.channel.send("teehee :P")
                return
    
    
    async def ping(self, message):
        if message.content == "ping":
            if random.randrange(10) < 1:
                await message.channel.send(":O ponggers")
                return True
        return False
    
        
    async def gpt2_chat(self, message):
        # This is the gpt2-chatbot channel.
        if not loadChatbot:
            return
            
        if message.channel.id == 762173542233407528:
            if random.randrange(5) < 1:
                async with message.channel.typing():
                    response = chatbot.get_response(message.content)
                    time.sleep(random.random() * 1)
                    await message.channel.send(response)
                    return True
        return False



client = MyClient()
client.run('NzYyMTY0MTkxNDEwNTIwMDk0.X3lKtw.Sqscgwss27OXVuAl4OJAWHQSoRE')