import Bot

bot = Bot()

# initialize state
bot.read_initialize()

# game loop
while True:
    print(bot.get_action(bot.read_state()))
