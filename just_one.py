import asyncio
from guess import judge_guess
import discord
import random
from discord import activity
from discord.abc import User
from discord.enums import Status
from discord.ext import commands
from game_data import game_data

token = open("token.txt",
             'r').read()
game = discord.Game("현재 대기")
bot = commands.Bot(command_prefix='!',
                   status=discord.Status.online, activity=game)

active_game = {}


async def confirm_hints(msg, current_game):
    hints = current_game.hints
    if msg.content == current_game.word:
        current_game.confirmed = True
    elif msg.content in hints:
        del hints[msg.content]
        await msg.channel.send(f"{msg.content}이(가) 삭제되었습니다.")


async def judge_answer(status, current_game):
    word = current_game.word
    guess = current_game.guess
    if status == "correct":
    	embed = discord.Embed(title="정답자가 정답을 맞추었습니다!",
    	                      description=f"정답은 {word}입니다.")
    elif status == "pass":
    	embed = discord.Embed(title="정답자가 패스를 선언하였습니다.",
    	                      description=f"정답은 {word}입니다.")
    else:
    	embed = discord.Embed(title="아쉽게도 정답을 맞히지 못했습니다.",
    	                      description=f"정답은 {word}이며, 추측한 답은 {guess}입니다.")
    	current_game.round -= 1
    embed.add_field(name="참가자들이 작성한 힌트들은 다음과 같습니다.",
                    value=current_game.submitted_hints)
    await current_game.main_channel.send(embed=embed)
    current_game.current_round += 1
    await start_round(current_game)


async def start_guessing(current_game):
    hints = current_game.hints
    embed = discord.Embed(title="이제 당신의 차례입니다!")
    str_hints = ""
    for hint in hints:
    	str_hints += f"{hint}({hints[hint][0]}), "
    str_hints = str_hints[:-2]
    embed.add_field(name="힌트들을 보고 답안을 DM으로 보내주세요!",
                    value="힌트는 메인 채널에서 확인할 수 있습니다.")
    embed.add_field(name="만약 패스를 하고 싶다면,", value="채팅창에 '패스'라고 입력해주세요!")
    await current_game.guesser.send(embed=embed)
    embed = discord.Embed(title="힌트 검수가 끝났습니다.",
                          description="정답자는 다음 힌트들을 보고 답을 DM으로 보내주세요!")
    embed.add_field(name="주어진 힌트들은 다음과 같습니다.",
                    value=f"{str_hints if str_hints else '힌트가 모두 사라졌습니다...'}")
    await current_game.main_channel.send(embed=embed)


async def start_round(current_game):
	current_game.hint_time = True
	current_game.hints = {}
	current_game.hint_submission = 0
	current_game.guesser = random.choice(current_game.members)
	current_game.word = random.choice(current_game.words)
	current_game.confirmed = False
	while current_game.word in current_game.already:
		current_game.word = random.choice(current_game.words)
	if current_game.current_round >= current_game.round:
		embed = discord.Embed(title="모든 게임이 종료되었습니다!")
		await current_game.main_channel.send(embed=embed)
		return
	await current_game.main_channel.send(f"이번 라운드의 정답자는 {current_game.guesser.name}입니다.")
	for member in current_game.members:
		if member == current_game.guesser:
			embed = discord.Embed(title="당신은 이번 라운드의 정답자입니다.",
			                      description="힌트 제공자들이 힌트를 줄 동안 잠시만 기다려주세요~")
		else:
			embed = discord.Embed(title="당신은 이번 라운드의 힌트 제공자입니다.",
			                      description=f"정답자가 제시어를 맞출 수 있도록 힌트 단어를 주세요. 제시어는 {current_game.word} 입니다.")
		await member.dm_channel.send(embed=embed)


async def start_game(current_game):
	current_game.start = True
	embed = discord.Embed(title="Just One 게임이 시작되었습니다!",
                       description="사용 방법을 설명드릴게요~")
	embed.add_field(name="힌트 제공자라면,",
	                value="제시어가 주어질 거에요! 정답자가 제시어를 맞출 수 있도록 한 단어짜리 힌트를 저에게 DM으로 보내주시면 됩니다. 결정적이어도 되지만, 겹친다면 힌트를 보여줄 수 없으니 최대한 겹치지 않도록 주세요!", inline=False)
	embed.add_field(
		name="정답자라면,", value="힌트 제공자들이 힌트를 비교한 후, 제가 힌트를 전해줄 거에요! 그 때 DM으로 정답으로 생각되는 단어를 적어주시면 됩니다!", inline=False)
	for member in current_game.members:
		if member.dm_channel:
			channel = member.dm_channel
		elif member.dm_channel is None:
			channel = await member.create_dm()
		await channel.send(embed=embed)
	await start_round(current_game)


@bot.command()
async def 시작(ctx):
    if ctx.channel.id in active_game:
        await ctx.send("이미 시작한 게임이 존재합니다.")
        return
    current_game = game_data()
    active_game[ctx.channel.id] = current_game
    current_game.main_channel = ctx
    game.name = "게임 진행"
    current_game.starter = ctx.message.author
    current_game.members.append(current_game.starter)
    current_game.start = True
    current_game.can_join = True
    await bot.change_presence(activity=discord.Game(name="게임 진행"))
    embed = discord.Embed(title="Just One에 오신 것을 환영합니다!",
                          desciption="Just One은 정답자에게 겹치지 않는 힌트를 줘야하는 협력 게임입니다. 제시어를 보고 다른 사람들이 적지 않을만한 힌트를 적어주세요!")
    embed.add_field(
        name="참가 방법", value="게임에 참가하고 싶다면 !참가를 입력해주세요.", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def 리셋(ctx):
    del active_game[ctx.channel.id]
    await ctx.send("게임이 초기화되었습니다.")


@bot.command()
async def 참가(ctx):
    if ctx.channel.id not in active_game:
        await ctx.send("현재 시작한 게임이 없습니다.")
        return
    current_game = active_game[ctx.channel.id]
    if current_game.can_join == True:
        player = ctx.message.author
        if player not in current_game.members:
            current_game.members.append(player)
            await ctx.send("{}님이 참가하셨습니다. 현재 플레이어 {}명".format(player.name, len(current_game.members)))
        else:
            await ctx.send("{}님은 이미 참가중입니다.".format(player.name))
    else:
        await ctx.send("참가가 이미 마감되었습니다.")


@bot.command()
async def 마감(ctx):
    current_game = active_game[ctx.channel.id]
    if len(current_game.members) < 3:
        await ctx.send("플레이어 수가 2명 이하입니다. 게임을 시작할 수 없습니다.")
        return
    if not current_game.round:
        await ctx.send("문제의 개수가 0개입니다. 단어 개수를 설정해주세요.")
        return
    if current_game.can_join:
        current_game.can_join = False
        await ctx.send("참가가 마감되었습니다.")
        await start_game(current_game)
    else:
        await ctx.send("현재 진행중인 게임이 없습니다.")


@bot.command()
async def 개수(ctx, number):
    current_game = active_game[ctx.channel.id]
    if current_game.can_join:
        current_game.round = int(number)
    await ctx.send(f'문제 개수가 {current_game.round}로 설정되었습니다.')


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    for channel_id in active_game:
        if message.author in active_game[channel_id].members:
            current_game = active_game[channel_id]
            break
    if message.author.bot:
        return
    if current_game.start == True and current_game.can_join == False:
        if message.channel.type.name == "private":
            if current_game.guesser == message.author:
                if not current_game.hint_time:  # 정답 추측
                    current_game.guess = message.content
                    if current_game.guess != "패스":
                        await current_game.main_channel.send("정답자가 정답을 제출하였습니다. 방장이 정답을 판단하고 있습니다.")
                        await judge_guess(current_game)
                    else:
                        await judge_answer("pass", current_game)
            else:
                if current_game.hint_time:  # 힌트 제시
                    if message.content in current_game.hints:
                        current_game.hints[message.content].append(message.author.name)
                    else:
                        current_game.hints[message.content] = [message.author.name]
                    current_game.hint_submission += 1
                    await current_game.main_channel.send(f"{message.author.name}님이 힌트를 제시하였습니다.")
                    await message.author.send(f"등록된 힌트: {message.content}")
                    # 힌트 검수 시작
                    if current_game.hint_submission >= len(current_game.members) - 1:
                        current_game.hint_time = False
                        await current_game.main_channel.send("모든 참가자가 힌트를 제시하였습니다. 방장이 힌트를 검수 중입니다.")
                        str_hints = ""
                        for hint in current_game.hints:
                            str_hints += f"{hint}{current_game.hints[hint]}, "
                        str_hints = str_hints[:-2]
                        current_game.submitted_hints = str_hints
                        embed = discord.Embed(title="이제 힌트를 검수할 차례입니다!")
                        embed.add_field(name="참가자들이 입력한 힌트는 다음과 같습니다.",
                                        value=str_hints, inline=False)
                        embed.add_field(name=f"힌트 검수가 끝났다면, 제시어 {current_game.word}을(를) DM으로 보내주세요!",
                                        value="단어를 삭제하고 싶다면, 똑같은 단어를 입력해주세요! 삭제된 힌트는 되돌릴 수 없으니 주의하시고요!", inline=False)
                        confirmer = current_game.members[1] if current_game.starter == current_game.guesser else current_game.starter
                        await confirmer.send(embed=embed)
                else:  # 힌트 검수 중
                    confirmer = current_game.members[1] if current_game.starter == current_game.guesser else current_game.starter
                    if message.author == confirmer:
                        await confirm_hints(message, current_game)  # 힌트 삭제
                    if current_game.confirmed:  # 힌트 검수 마감
                        await current_game.main_channel.send("방장이 검수를 마쳤습니다. 정답자가 정답을 추측 중입니다.")
                        await start_guessing(current_game)

@bot.event
async def on_raw_reaction_add(payload):
    for channel_id in active_game:
        for member in active_game[channel_id].members:
            if payload.user_id == member.id:
                current_game = active_game[channel_id]
                break
    confirmer = current_game.members[1] if current_game.starter == current_game.guesser else current_game.starter
    if confirmer.id == payload.user_id:
        if str(payload.emoji) == "⭕":
            await judge_answer("correct", current_game)
        elif str(payload.emoji) == "❌":
            await judge_answer("wrong", current_game)
bot.run(token)
