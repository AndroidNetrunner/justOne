import discord
from start_round import start_round
from utils import get_submitted_hints


async def correct_answer(current_game):
    embed = discord.Embed(
        title="정답자가 정답을 맞추었습니다!", description=f"정답은 {current_game.word}입니다."
    )
    current_game.correct += 1
    await notify_result(current_game, embed)


async def wrong_answer(current_game):
    embed = discord.Embed(
        title="아쉽게도 정답을 맞히지 못했습니다.",
        description=f"정답은 {current_game.word}이며, 추측한 답은 {current_game.guess}입니다.",
    )
    current_game.round -= 1
    await notify_result(current_game, embed)


async def declare_pass(current_game):
    embed = discord.Embed(
        title="정답자가 패스를 선언하였습니다.", description=f"정답은 {current_game.word}입니다."
    )
    await notify_result(current_game, embed)


async def notify_result(current_game, embed):
    embed.add_field(name="참가자들이 작성한 힌트들은 다음과 같습니다.", value=current_game.submitted_hints)
    await current_game.main_channel.send(embed=embed)
    for member in current_game.members:
        await member.send(embed=embed)
    current_game.current_round += 1
    await start_round(current_game)


async def judge_guess(game_data):
    await game_data.main_channel.send("정답자가 정답을 제출하였습니다. 방장이 정답을 판단하고 있습니다.")
    embed = discord.Embed(title="정답자가 추측을 끝냈습니다.", description="이제 정답인지 아닌지 판단하실 때입니다!")
    embed.add_field(
        name=f"정답자가 추측한 답은 {game_data.guess}이고, 제시어는 {game_data.word}입니다.",
        value=f"정답이라고 생각하신다면 ⭕를, 틀렸다고 생각하시면 ❌를 눌러주세요!",
    )
    confirmer = (
        game_data.members[1]
        if game_data.starter == game_data.guesser
        else game_data.starter
    )
    msg = await confirmer.send(embed=embed)
    await msg.add_reaction("⭕")
    await msg.add_reaction("❌")


async def submit_guess(current_game, message):
    if current_game.hint_time:
        return
    current_game.guess = message.content
    if current_game.guess != "패스":
        await judge_guess(current_game)
    else:
        await declare_pass(current_game)


async def start_guessing(current_game):
    for member in current_game.members:
        embed = discord.Embed(title="힌트가 모두 확정되었습니다!")
        str_hints = get_submitted_hints(current_game)
        embed.add_field(
            name="정답자는 힌트를 보고 정답을 DM으로 제출해주세요.",
            value=f"힌트: {str_hints if str_hints else '힌트가 모두 사라졌습니다...'}",
            inline=False,
        )
        embed.add_field(name="만약 패스를 하고 싶다면,", value="채팅창에 '패스'라고 입력해주세요!")
        await member.send(embed=embed)
    embed = discord.Embed(
        title="힌트 검수가 끝났습니다.", description="정답자는 다음 힌트들을 보고 답을 DM으로 보내주세요!"
    )
    embed.add_field(
        name="주어진 힌트들은 다음과 같습니다.",
        value=f"{str_hints if str_hints else '힌트가 모두 사라졌습니다...'}",
    )
    await current_game.main_channel.send(embed=embed)
