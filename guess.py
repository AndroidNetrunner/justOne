import discord
import start_round

async def judge_answer(status, current_game):
    word = current_game.word
    guess = current_game.guess
    if status == "correct":
        embed = discord.Embed(title="정답자가 정답을 맞추었습니다!",
                                description=f"정답은 {word}입니다.")
        current_game.correct += 1
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

async def judge_guess(game_data):
    await game_data.main_channel.send("정답자가 정답을 제출하였습니다. 방장이 정답을 판단하고 있습니다.")
    embed = discord.Embed(title="정답자가 추측을 끝냈습니다.", description="이제 정답인지 아닌지 판단하실 때입니다!")
    embed.add_field(name=f"정답자가 추측한 답은 {game_data.guess}이고, 제시어는 {game_data.word}입니다.", value=f"정답이라고 생각하신다면 ⭕를, 틀렸다고 생각하시면 ❌를 눌러주세요!")
    confirmer = game_data.members[1] if game_data.starter == game_data.guesser else game_data.starter
    msg = await confirmer.send(embed=embed)
    await msg.add_reaction("⭕")
    await msg.add_reaction("❌")

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