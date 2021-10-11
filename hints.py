import asyncio
import discord

async def submit_hint(current_game, message):
    for word in current_game.hints:
        if message.author.name in current_game.hints[word]:
            current_game.hints[word].remove(message.author.name)
            current_game.hint_submission -= 1
            if not current_game.hints[word]:
                del current_game.hints[word]
            break
    if message.content in current_game.hints:
        current_game.hints[message.content].append(message.author.name)
    else:
        current_game.hints[message.content] = [message.author.name]
    current_game.hint_submission += 1
    await current_game.main_channel.send(f"{message.author.name}님이 힌트를 제시하였습니다.")
    await message.author.send(f"등록된 힌트: {message.content}")

async def start_checking_hints(current_game):
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

async def confirm_hints(msg, current_game):
    hints = current_game.hints
    if msg.content == current_game.word:
        current_game.confirmed = True
    elif msg.content in hints:
        del hints[msg.content]
        await msg.channel.send(f"{msg.content}이(가) 삭제되었습니다.")
