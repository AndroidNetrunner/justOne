import discord
from start_round import start_round

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