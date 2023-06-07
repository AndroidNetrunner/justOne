import random
import discord
from game_data import active_game

async def start_round(current_game):
    await reset_round(current_game)
    if current_game.current_round >= current_game.round:
        return await show_result(current_game)
    await current_game.main_channel.send(f"{current_game.current_round + 1} 라운드의 정답자는 {current_game.guesser.name}입니다.")
    await notify_role_to_players(current_game)
    
async def reset_round(current_game):
    current_game.hint_time = True
    current_game.hints = {}
    current_game.hint_submission = 0
    if not current_game.remained_guesser_candidate:
        current_game.remained_guesser_candidate = current_game.members[:]
        random.shuffle(current_game.remained_guesser_candidate)
    current_game.guesser = current_game.remained_guesser_candidate.pop()
    current_game.word = random.choice(current_game.words)
    current_game.confirmed = False
    while current_game.word in current_game.already:
        current_game.word = random.choice(current_game.words)
    current_game.already.add(current_game.word)

async def show_result(current_game):
    del active_game[current_game.main_channel.channel.id]
    embed = discord.Embed(title="모든 게임이 종료되었습니다!", description=f"{current_game.round}개의 문제 중 {current_game.correct}개의 정답을 맞추셨습니다.")
    await current_game.main_channel.send(embed=embed)

async def notify_role_to_players(current_game):
    for member in current_game.members:
        if member == current_game.guesser:
            embed = discord.Embed(title="당신은 이번 라운드의 정답자입니다.",
                                    description="힌트 제공자들이 힌트를 줄 동안 잠시만 기다려주세요~")
        else:
            embed = discord.Embed(title="당신은 이번 라운드의 힌트 제공자입니다.",
                                    description=f"정답자가 제시어를 맞출 수 있도록 힌트 단어를 주세요. 제시어는 {current_game.word} 입니다.")
        await member.dm_channel.send(embed=embed)