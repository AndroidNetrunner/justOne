import discord
async def judge_guess(game_data):
	embed = discord.Embed(title="정답자가 추측을 끝냈습니다.", description="이제 정답인지 아닌지 판단하실 때입니다!")
	embed.add_field(name=f"정답자가 추측한 답은 {game_data.guess}이고, 제시어는 {game_data.word}입니다.", value=f"정답이라고 생각하신다면 ⭕를, 틀렸다고 생각하시면 ❌를 눌러주세요!")
	confirmer = game_data.members[1] if game_data.starter == game_data.guesser else game_data.starter
	msg = await confirmer.send(embed=embed)
	await msg.add_reaction("⭕")
	await msg.add_reaction("❌")