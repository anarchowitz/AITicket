import asyncio, requests, time, difflib, discord
from discord.ext import commands

DISCORD_TOKEN = 'suck_my_balls'

intents = discord.Intents.default()
intents.message_content = True
intents.typing = True  # Optional: set to True if your bot needs to see typing status
intents.presences = True  # Optional: set to True if your bot needs to see presence updates
intents.members = True  # Optional: set to True if your bot needs to see member info
bot = commands.Bot(command_prefix='!', intents=intents)

qa_pairs_url = 'https://raw.githubusercontent.com/Anarchowitz/AITicket/main/qa_pairs.txt'
whitelist_nicks_url = 'https://raw.githubusercontent.com/Anarchowitz/AITicket/main/whitelist_nick.txt'

qa_pairs = {}
response = requests.get(qa_pairs_url)
for line in response.text.splitlines():
    parts = line.strip().split('|')
    if len(parts) == 2:
        question, answer = parts
        qa_pairs[question.strip().lower()] = answer.strip()
    else:
        print(f"Skipping invalid line: {line}")

whitelist_nicks = []
response = requests.get(whitelist_nicks_url)
for line in response.text.splitlines():
    for nick in line.strip().split(','):
        whitelist_nicks.append(nick.strip().lower())

ticket_status = {}

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("yooma.su"))
    print(f'{bot.user} подключился к Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.channel.name.startswith('ticket-'):
        print(f'Новое сообщение в тикете {message.channel.name}: {message.content}')
        if message.author.name.lower() in whitelist_nicks:
            if message.content.startswith('!stop'):
                ticket_status[message.channel.id] = False
                await message.channel.send('Бот остановлен в этом тикете.')
                await message.add_reaction('✅')
                return
            if message.content.startswith('!start'):
                ticket_status[message.channel.id] = True
                await message.channel.send('Бот запущен в этом тикете.')
                await message.add_reaction('✅')
                return
        else:
            if message.channel.id not in ticket_status or ticket_status[message.channel.id]:
                if message.clean_content.lower() == "welcome":  # ignore "Welcome" messages
                    return
                question = message.content.strip().lower().rstrip('?')
                possible_questions = list(qa_pairs.keys())
                best_match = max(possible_questions, key=lambda x: difflib.SequenceMatcher(None, x, question).ratio())
                if difflib.SequenceMatcher(None, best_match, question).ratio() > 0.6:  # adjust the threshold as needed
                    answer = qa_pairs[best_match]
                    await message.channel.send(answer)
                else:
                    await message.channel.send("Ошибка: Попробуйте перефразировать свой вопрос. Если это не ошибка, ожидайте модератора. ")

if __name__ == "__main__":
    async def main():
        await bot.start(DISCORD_TOKEN)
    asyncio.run(main())
