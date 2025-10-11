import aiohttp, asyncio, datetime, discord, dotenv, json, logging, os, random, re, sys
# logging.basicConfig(level=logging.DEBUG)

dotenv.load_dotenv()
activity = os.getenv("ACTIVITY") # str
ai_token = os.getenv("AI_TOKEN") # str
chance = float(os.getenv("CHANCE")) # FLOAT
context = int(os.getenv("CONTEXT")) # INT
default_prompt = os.getenv("DEFAULT_PROMPT") # str
discord_token = os.getenv("DISCORD_TOKEN") # str
prompt_end = os.getenv("PROMPT_END") # str
reply_to_bots = os.getenv("REPLY_TO_BOTS") != "False" # BOOL :trollface:

bot = discord.Client(intents=discord.Intents.all())
tree = discord.app_commands.CommandTree(bot)

votebans = {}
prompts = {}

# The script is awful so thanks for reading that
# With Russian commands, the coder knows no disgrace
# Fuck indentation, my bot is running still
# Shitcode is calling to all men who use Deepseek

# On second thought this is not so rhythmic. But it's as terrible as the code, so it's fine.

async def ban(member, time):
    print(f"Trying to ban {member.display_name}.")
    try:
        await member.timeout(datetime.datetime.now(datetime.UTC) + time)
        print(f"{bot.user.display_name} banned {member.display_name} на {time}.")
    except: pass

class votebanc: # c for class
    def __init__ (self, banned, time, starter):
        self.voters = [starter, banned]
        self.time = time
        self.score = 0

async def process_bans():
    while True:
        global votebans
        for channel in votebans:
            await channel.send(f"Голосование за бан <@{votebans[channel].voters[1].id}> закончилось со счётом {votebans[channel].score}.") # Hardcoded Russian lol
            if votebans[channel].score > 2: await ban(votebans[channel].voters[1], votebans[channel].time)
            if votebans[channel].score < 0: await ban(votebans[channel].voters[0], votebans[channel].time)
        votebans = {}
        await asyncio.sleep(120)

try:
    with open("prompts.json", "r") as f: prompts = json.load(f)
except:
    with open("prompts.json", "w") as f: json.dump({}, f)

def setpromptbeh(prompt, server):
    prompts[server] = prompt
    with open("prompts.json", "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False)

async def askai(channel): # GOIDA
    messages = [msg async for msg in channel.history(limit=context)]
    async with channel.typing(), aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session, session.post("https://api.deepseek.com/v1/chat/completions", headers={"Authorization": f"Bearer {ai_token}"}, json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompts.get(str(channel.guild.id), default_prompt) + prompt_end + "\n".join(f"{msg.author.display_name} ({msg.author.id}): {msg.content}" for msg in reversed(messages))}]}) as response: return (await response.json())["choices"][0]["message"]["content"]

async def tryban(bot_message):
    match = re.search(r"/kill\s+(\d{17,19})", bot_message.content) # Я не ебу как работает регекс
    if match: await ban(await bot_message.guild.fetch_member(int(match.group(1))), datetime.timedelta(seconds=15))

@bot.event
async def on_ready():
    for guild in bot.guilds: await tree.sync(guild=guild)
    await bot.change_presence(activity=discord.Game(name=activity))
    print(f'{bot.user} is running.')
    bot.loop.create_task(console_input())
    bot.loop.create_task(process_bans())

@bot.event
async def on_message(message):
    if message.guild is None or message.author == bot.user or (message.author.bot and not reply_to_bots) or (not (bot.user in message.mentions or random.random() < chance)): return

    try:
        response = await askai(message.channel)
        bot_message = await message.reply(response)
        print(f"{message.guild.name} ({message.guild.id}) > {message.channel} ({message.channel.id}) > {message.author.display_name} ({message.author.id}): {message.content}")
        print(f"{bot.user.display_name} responded: {response}")
        await tryban(bot_message)
    except: pass

async def console_input():
    while True:
        text = await asyncio.get_event_loop().run_in_executor(None, input, "ඞ ") # a very sus ps1
        parts = text.split(" ")
        try:
            match parts[0]:
                case "restart": os.execv(sys.executable, [sys.executable] + sys.argv)
                case "send": await bot.get_channel(int(parts[1])).send(" ".join(parts[2:]))
                case "setprompt": setpromptbeh(" ".join(parts[2:]), parts[1])
                case "prompts": print(prompts.items())
                case "reply": await bot.get_channel(int(parts[1])).send(await askai(bot.get_channel(int(parts[1]))))
                case _: raise Exception()
        except: print("restart, send *channel* *message*, setprompt *server* *prompt*, prompts, reply *channel*")

@tree.command(name="restart", description="Рестартает бота")
@discord.app_commands.default_permissions(administrator=True)
async def restart(interaction):
    if interaction.guild is None: return
    await interaction.response.send_message("Рестарт...")
    print(f"{interaction.guild.name} ({interaction.guild.id}) > {interaction.channel.name} ({interaction.channel.id}) > {interaction.user.display_name} ({interaction.user.id}): /restart")
    os.execv(sys.executable, [sys.executable] + sys.argv)

@tree.command(name="send", description="Присылает сообщение в этот канал от имени бота")
@discord.app_commands.default_permissions(administrator=True)
async def send(interaction, message: str):
    if interaction.guild is None: return
    print(f"{interaction.guild.name} ({interaction.guild.id}) > {interaction.channel.name} ({interaction.channel.id}) > {interaction.user.display_name} ({interaction.user.id}): /send")
    print(f"{bot.user.display_name} responded: {message}")
    await interaction.response.send_message(message)

@tree.command(name="setprompt", description="Меняет промпт бота")
@discord.app_commands.default_permissions(administrator=True)
async def setprompt(interaction, prompt: str):
    if interaction.guild is None: return
    await interaction.response.send_message("Промпт изменён.")
    print(f"{interaction.guild.name} ({interaction.guild.id}) > {interaction.channel.name} ({interaction.channel.id}) > {interaction.user.display_name} ({interaction.user.id}): /setprompt {prompt}")
    setpromptbeh(prompt, str(interaction.guild.id))

@tree.command(name="prompt", description="Отображает текущий промпт бота")
async def prompt(interaction):
    if interaction.guild is None: return
    print(f"{interaction.guild.name} ({interaction.guild.id}) > {interaction.channel.name} ({interaction.channel.id}) > {interaction.user.display_name} ({interaction.user.id}): /prompt")
    print(f"{bot.user.display_name} responded: {prompts.get(str(interaction.guild.id), default_prompt)}")
    await interaction.response.send_message(prompts.get(str(interaction.guild.id), default_prompt))

@tree.command(name="voteban", description="Устраивает демократию. 0 минут = разбан")
async def voteban(interaction, id: str, minutes: int):
    if interaction.guild is None: return
    print(f"{interaction.guild.name} ({interaction.guild.id}) > {interaction.channel.name} ({interaction.channel.id}) > {interaction.user.display_name} ({interaction.user.id}): /voteban {id} {minutes}")
    if interaction.channel in votebans.keys():
        await interaction.response.send_message(f"В этом канале уже идёт голосование за бан {votebans[interaction.channel].voters[1].display_name}")
        return
    try: banned = await interaction.guild.fetch_member(int(id))
    except: banned = None
    if not banned or banned == interaction.user:
        await interaction.response.send_message(f"Некоректный айди - <@{id}>")
        return
    if int(minutes) > 15 or int(minutes) < 0:
        await interaction.response.send_message(f"Нельзя таймаутить на {minutes} минут, нужно от 0 до 15.")
        return
    votebans[interaction.channel] = votebanc(banned, datetime.timedelta(minutes=int(minutes)), interaction.user)
    await interaction.response.send_message(f"Запущено голосование на таймаут <@{id}> на {minutes} минут. Оно продлится 1 минуту. Необходим перевес в 3 голоса. Если перевес будет отрицателен, в таймаут полетит инициатор. Используйте /yes и /no")
    print(f"{interaction.user.display_name} started a vote to ban {banned.display_name} for {minutes} minutes.")

@tree.command(name="yes", description="Голосует за Единую Россию")
async def yes(interaction):
    if interaction.guild is None: return
    print(f"{interaction.guild.name} ({interaction.guild.id}) > {interaction.channel.name} ({interaction.channel.id}) > {interaction.user.display_name} ({interaction.user.id}): /yes")
    if not interaction.channel in votebans.keys():
        await interaction.response.send_message("В этом канале нет активного голосования.")
        return
    if interaction.user in votebans[interaction.channel].voters:
        await interaction.response.send_message("Ты либо уже голосовал, либо ты инициатор или цель.")
        return
    votebans[interaction.channel].voters.append(interaction.user)
    votebans[interaction.channel].score = votebans[interaction.channel].score + 1
    await interaction.response.send_message(f"Голос за бан {votebans[interaction.channel].voters[1].display_name} успешно учтён. Текущий счёт: {votebans[interaction.channel].score}")

@tree.command(name="no", description="Тоже голосует за Единую Россию")
async def no(interaction):
    if interaction.guild is None: return
    print(f"{interaction.guild.name} ({interaction.guild.id}) > {interaction.channel.name} ({interaction.channel.id}) > {interaction.user.display_name} ({interaction.user.id}): /no")
    if not interaction.channel in votebans.keys():
        await interaction.response.send_message("В этом канале нет активного голосования.")
        return
    if interaction.user in votebans[interaction.channel].voters:
        await interaction.response.send_message("Ты либо уже голосовал, либо ты инициатор или цель.")
        return
    votebans[interaction.channel].voters.append(interaction.user)
    votebans[interaction.channel].score = votebans[interaction.channel].score - 1
    await interaction.response.send_message(f"Голос против бана {votebans[interaction.channel].voters[1].display_name} успешно учтён. Текущий счёт: {votebans[interaction.channel].score}")

bot.run(discord_token)
