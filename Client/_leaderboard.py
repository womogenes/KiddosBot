from tabulate import tabulate
import time

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
signify = lambda x: "+" + str(x) if x > 0 else x

async def clear_leaderboard(self):
    async for m in self.leaderboardChannel.history():
        if m.id not in self.lbMessages:
            await m.delete()
    
    
async def clean_leaderboard(self, message):
    if message.channel.id != 763825477533302856:
        return
        
    if message.id not in self.lbMessages:
        await message.delete()
        

async def update_leaderboard(self):
    if time.time() - self.lastUpdatedLeaderboard < 60:
        return
    self.lastUpdatedLeaderboard = time.time()
    
    # By lifetime points.
    table1 = [["Rank", "Name", "Points"]]
    tp = sorted(self.points["lifetime"], key=lambda x: self.points["lifetime"][x], reverse=True)
    for i in range(len(tp)):
        user = await self.fetch_user(tp[i])
        table1.append([ordinal(i + 1), user.display_name, self.points["lifetime"][tp[i]]])
    
    text1 = tabulate(table1, headers="firstrow", tablefmt="github", numalign="left")
    
    # By weekly points.
    table2 = [["Rank", "Name", "Points"]]
    tw = sorted(self.points["weekly"], key=lambda x: self.points["weekly"][x], reverse=True)
    for i in range(len(tw)):
        user = await self.fetch_user(tw[i])
        x = self.points["weekly"][tw[i]]
        table2.append([ordinal(i + 1), user.display_name, signify(self.points["weekly"][tw[i]])])
    
    text2 = tabulate(table2, headers="firstrow", tablefmt="github", numalign="left")
    
    # By hitrate.
    table3 = [["Rank", "Name", "Correct/Total", "Accuracy"]]
    def hitrate(x):
        if self.points["hitrate"][x][1] < 10:
            return 0
        return self.points["hitrate"][x][0] / self.points["hitrate"][x][1]
        
    ac = sorted(self.points["weekly"], key=hitrate, reverse=True)
    for i in range(len(ac)):
        user = await self.fetch_user(ac[i])
        percent = 0 if self.points["hitrate"][user.id][1] == 0 else self.points["hitrate"][user.id][0] / self.points["hitrate"][user.id][1]
        percentage = str(round(percent * 100, 1)) + "%"
        outof = f"{self.points['hitrate'][user.id][0]}/{self.points['hitrate'][user.id][1]}"
        table3.append([ordinal(i + 1), user.display_name, outof, percentage])
    
    text3 = tabulate(table3, headers="firstrow", tablefmt="github", numalign="left")
    
    text1 = f"**Sorted by lifetime points:**\n```{text1}```"
    text2 = f"**Sorted by this week's points:**\n```{text2}```"
    text3 = f"**Sorted by accuracy:**\n```{text3}```"
    
    message1 = await self.leaderboardChannel.fetch_message(self.lbMessages[0])
    await message1.edit(content=text1)
    
    message2 = await self.leaderboardChannel.fetch_message(self.lbMessages[1])
    await message2.edit(content=text2)
    
    message3 = await self.leaderboardChannel.fetch_message(self.lbMessages[2])
    await message3.edit(content=text3)
    
    self.lastUpdatedLeaderboard = time.time()
    print("UPDATED LEADERBOARDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")