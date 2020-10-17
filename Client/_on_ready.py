async def on_ready(self):
    """
    This function is called when the client is ready.
    """
    print("Logged on as " + str(self.user) + "!")
    self.initialize()
    await self.send_quote()
    await self.update_leaderboard()
    await self.replenish_cache()
    print("Question cache ready!")
    await self.clear_leaderboard()