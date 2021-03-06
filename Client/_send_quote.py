import time
import json
from datetime import datetime as dt
import requests

async def send_quote(self):
    if dt.strptime(next(self.db.dateInfo.find({}))["last-sent-quote"], "%Y-%m-%d %H:%M:%S.%f").date() != dt.now().date():
        url = 'https://quotes.rest/qod?category=inspire'
        api_token = "X-TheySaidSo-Api-Secret"
        headers = {
            "content-type": "application/json",
            "X-TheySaidSo-Api-Secret": format(api_token)
        }

        response = requests.get(url, headers=headers)
        quotes = response.json()["contents"]["quotes"][0]
        
        # Spammy quotes!
        await self.quoteChannel.send(f"""**Quote of the day:**\n\n> {quotes["quote"]}\n\n~ *{quotes["author"]}*""")
        
        self.db.dateInfo.update_one({}, {"$set": {"last-sent-quote": str(dt.now())}})