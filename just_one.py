import asyncio
import discord
import random
from discord import activity
from discord.abc import User
from discord.enums import Status
from discord.ext import commands

token = open("C:/Users/byukim/Documents/python/discord_bot/Just one/token.txt",
             'r').read()
game = discord.Game("현재 대기")
bot = commands.Bot(command_prefix='!',
                   status=discord.Status.online, activity=game)
members = []
round = 13
hints = {}
words = open("C:/Users/byukim/Documents/python/discord_bot/Just one/word_list.txt",
             'r', encoding='UTF-8').read().split('\n')
already = []
guesser = None
main_channel = None
guess = None
start = False
hint_time = False
starter = None
word = None
confirmed = None
checking = False
judged_hints = {}

async def confirm_hints(msg, hints):
	global word
	global confirmed
	if msg == word:
		confirmed = True
	elif msg in hints:
		del hints[msg]

async def judge_answer(status, guess, word):
	global main_channel
	global round
	global hints
	if status == "correct":
		embed = discord.Embed(title="정답자가 정답을 맞추었습니다!", description=f"정답은 {word}입니다.")
	elif status == "pass":
		embed = discord.Embed(title="정답자가 패스를 선언하였습니다.", description=f"정답은 {word}입니다.")
	else:
		embed = discord.Embed(title="아쉽게도 정답을 맞히지 못했습니다.", description=f"정답은 {word}이며, 추측한 답은 {guess}였습니다.")
		round -= 1
	embed.add_field(name="참가자들이 작성한 힌트들은 다음과 같습니다.", value=hints)
	await main_channel.send(embed=embed)

def judge_hints(hints):
	global starter
	for word in hints:
		if len(hints[word]) != 1:
			del hints[word]
	return hints
		
async def start_guessing(hints):
	global guesser
	embed = discord.Embed(title="이제 당신의 차례입니다!")
	str_hints = ""
	for hint in hints:
		str_hints += f"{hint}({hints[hint][0]}), "
	str_hints = str_hints[:-2]
	embed.add_field(name="힌트들을 보고 제시어를 DM으로 보내주세요!", value=f"힌트는 {str_hints}입니다.")
	embed.add_field(name="만약 패스를 하고 싶다면,", value="채팅창에 '패스'라고 입력해주세요!")
	await guesser.send(embed=embed)

async def start_round(num):
	global hint_time
	global hints
	global guesser
	global word

	hint_time = True
	hints = {}
	word = random.choice(words)
	while word in already:
		word = random.choice(words)
	if num >= round:
		embed = discord.Embed(title="모든 게임이 종료되었습니다!")
		await main_channel.send()
		return
	for member in members:
		if member == guesser:
			embed = discord.Embed(title="당신은 이번 라운드의 정답자입니다.",
			                      description="힌트 제공자들이 힌트를 줄 동안 잠시만 기다려주세요~")
		else:
			embed = discord.Embed(title="당신은 이번 라운드의 힌트 제공자입니다.",
			                      description=f"정답자가 제시어를 맞출 수 있도록 힌트 단어를 주세요. 제시어는 {word} 입니다.")
		await member.dm_channel.send(embed=embed)
	
async def start_game():
	global start
	global guesser
	start = True
	embed = discord.Embed(title="Just One 게임이 시작되었습니다!",
                       description="사용 방법을 설명드릴게요~")
	embed.add_field(name="힌트 제공자라면,",
	                value="제시어가 주어질 거에요! 정답자가 제시어를 맞출 수 있도록 한 단어짜리 힌트를 주시면 됩니다. 결정적이어도 되지만, 겹친다면 힌트를 보여줄 수 없으니 최대한 겹치지 않도록 주세요!")
	embed.add_field(
		name="정답자라면,", value="힌트 제공자들이 힌트를 비교한 후, 제가 힌트를 전해줄 거에요! 그 때 DM으로 정답으로 생각되는 단어를 적어주시면 됩니다!")
	for member in members:
		if member.dm_channel:
			channel = member.dm_channel
		elif member.dm_channel is None:
			channel = await member.create_dm()
		await channel.send(embed=embed)
	guesser = random.choice(members)
	await start_round(0)


@bot.command()
async def 시작(ctx):
    global main_channel
    global can_join
    global start
    global starter

    main_channel = ctx
    game.name = "게임 진행"
    starter = ctx.message.author
    members.append(starter)
    start = True
    can_join = True
    embed = discord.Embed(title="Just One에 오신 것을 환영합니다!",
                          desciption="Just One은 정답자에게 겹치지 않는 힌트를 줘야하는 협력 게임입니다. 제시어를 보고 다른 사람들이 적지 않을만한 힌트를 적어주세요!")
    embed.add_field(
        name="참가 방법", value="게임에 참가하고 싶다면 !참가를 입력해주세요.", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def 참가(ctx):
    global can_join
    if can_join == True:
        player = ctx.message.author
        if player not in members:
            members.append(player)
            await ctx.send("{}님이 참가하셨습니다. 현재 플레이어 {}명".format(player.name, len(members)))
        else:
            await ctx.send("{}님은 이미 참가중입니다.".format(player.name))
    else:
        await ctx.send("참가가 이미 마감되었습니다.")


@bot.command()
async def 마감(ctx):
	global can_join
	global round
	# if len(members) < 3:
	# 	await ctx.send("플레이어 수가 2명 이하입니다. 게임을 시작할 수 없습니다.")
	# 	return
	if not round:
		await ctx.send("문제의 개수가 0개입니다. 단어 개수를 설정해주세요.")
		return
	if can_join == True:
		can_join = False
		await ctx.send("참가가 마감되었습니다.")
		await start_game()
	else:
		await ctx.send("현재 진행중인 게임이 없습니다.")


@bot.command()
async def 개수(ctx, number):
    global can_join
    global round
    if can_join:
        round = int(number)
    await ctx.send(f'문제 개수가 {round}로 설정되었습니다.')


@bot.event
async def on_message(message):
	global guesser
	global guess
	global start
	global hints
	global hint_time
	global word
	global confirmed
	global members
	global checking
	global judged_hints
	await bot.process_commands(message)
	if message.author.bot:
		return
	if start == True and can_join == False:
		if message.channel.type.name == "private":
			if guesser == message.author:
				if not hint_time:
					guess = message.content
					if guess != "패스":
						embed = discord.Embed(title="정답자가 추측을 끝냈습니다.", description="이제 정답인지 아닌지 판단하실 때입니다!")
						embed.add_field(name=f"정답자가 추측한 답은 {guess}이고, 제시어는 {word}입니다.", value=f"정답이라고 생각하신다면 ⭕를, 틀렸다고 생각하시면 ❌를 눌러주세요!")
						confirmer = members[1] if starter == guesser else starter
						msg = await confirmer.send(embed=embed)
						await msg.add_reaction("⭕")
						await msg.add_reaction("❌")
						checking = True
					else:
						judge_answer("pass", guess, word) 
			else:
				if hint_time:
					if message.content in hints:
						hints[message.content].append(message.author)
					else:
						hints[message.content] = [message.author.name]
					if len(hints) >= len(members) - 1:
						hint_time = False
						judged_hints = judge_hints(hints)
						await main_channel.send("모든 참가자가 힌트를 제시하였습니다. 방장이 힌트를 검수 중입니다.")
						str_hints = ""
						for hint in judged_hints:
							str_hints += f"{hint}({judged_hints[hint][0]}), "
						str_hints = str_hints[:-2]
						embed = discord.Embed(title="이제 힌트를 검수할 차례입니다!")
						embed.add_field(name="참가자들이 입력한 힌트는 다음과 같습니다.", value=str_hints)
						embed.add_field(name=f"힌트 검수가 끝났다면, 제시어 {word}을(를) DM으로 보내주세요!", value="단어를 삭제하고 싶다면, 똑같은 단어를 입력해주세요! 삭제된 힌트는 되돌릴 수 없으니 주의하시고요!")
						confirmer = members[1] if starter == guesser else starter 
						await confirmer.send(embed=embed)
				else:
					confirmer = members[1] if starter == guesser else starter
					if message.author == confirmer:
						await confirm_hints(message.content, judged_hints)
					if confirmed:
						await main_channel.send("방장이 검수를 마쳤습니다. 정답자가 정답을 추측 중입니다.")
						await start_guessing(hints)	

@bot.event
async def on_raw_reaction_add(payload):
	global guess
	global word
	global checking
	global guesser
	global starter
	confirmer = members[1] if starter == guesser else starter
	if confirmer.id == payload.user_id:
		if str(payload.emoji) == "⭕":
			await judge_answer("correct", guess, word)
			checking = False
		elif str(payload.emoji) == "❌":
			await judge_answer("wrong", guess, word)
			checking = False
bot.run(token)
