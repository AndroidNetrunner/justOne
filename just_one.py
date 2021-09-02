import asyncio
from utils import find_game_of_this_channel
import discord
import random
from discord import activity
from discord.abc import User
from discord.enums import Status
from discord.ext import commands
from game_data import game_data, active_game
from guess import judge_guess, start_guessing, judge_answer
from start_game import start_game
from start_round import start_round
from hints import submit_hint, check_hints, confirm_hints

token = open("token.txt",
             'r').read()
game = discord.Game("현재 대기")
bot = commands.Bot(command_prefix='~',
                   status=discord.Status.online, activity=game)

@bot.command()
async def 시작(ctx):
    if ctx.channel.id in active_game:
        await ctx.send("이미 시작한 게임이 존재합니다.")
        return
    current_game = game_data()
    active_game[ctx.channel.id] = current_game
    current_game.main_channel = ctx
    current_game.starter = ctx.message.author
    current_game.members.append(current_game.starter)
    current_game.start = True
    current_game.can_join = True
    await bot.change_presence(activity=discord.Game(name="게임 진행"))
    embed = discord.Embed(title="Just One에 오신 것을 환영합니다!",
                          desciption="Just One은 정답자에게 겹치지 않는 힌트를 줘야하는 협력 게임입니다. 제시어를 보고 다른 사람들이 적지 않을만한 힌트를 적어주세요!")
    embed.add_field(
        name="참가 방법", value="게임에 참가하고 싶다면 ~참가를 입력해주세요.", inline=False)
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
    current_game = find_game_of_this_channel(active_game, message.author.id)
    if message.author.bot or not current_game:
        return
    if current_game.start == True and current_game.can_join == False:
        if message.channel.type.name == "private":
            if current_game.guesser == message.author:
                if not current_game.hint_time:  # 정답 추측
                    current_game.guess = message.content
                    if current_game.guess != "패스":
                        await judge_guess(current_game)
                    else:
                        await judge_answer("pass", current_game)
            else:
                if current_game.hint_time:  # 힌트 제시
                    submit_hint(current_game, message)
                    # 힌트 검수 시작
                    if current_game.hint_submission >= len(current_game.members) - 1:
                        check_hints(current_game)
                else:  # 힌트 검수 중
                    confirmer = current_game.members[1] if current_game.starter == current_game.guesser else current_game.starter
                    if message.author == confirmer:
                        await confirm_hints(message, current_game)  # 힌트 삭제
                    if current_game.confirmed:  # 힌트 검수 마감
                        await current_game.main_channel.send("방장이 검수를 마쳤습니다. 정답자가 정답을 추측 중입니다.")
                        await start_guessing(current_game)

@bot.event
async def on_raw_reaction_add(payload):
    current_game = find_game_of_this_channel(active_game, payload.user_id)
    if not current_game:
        return
    confirmer = current_game.members[1] if current_game.starter == current_game.guesser else current_game.starter
    if confirmer.id == payload.user_id:
        if str(payload.emoji) == "⭕":
            await judge_answer("correct", current_game)
        elif str(payload.emoji) == "❌":
            await judge_answer("wrong", current_game)
bot.run(token)
