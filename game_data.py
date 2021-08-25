class game_data:
	def __init__(self):
		self.members = []
		self.round = 13
		self.hints = {}
		self.words = open("word_list.txt", 'r', encoding='UTF-8').read().split('\n')
		self.already = []
		self.guesser = None
		self.main_channel = None
		self.guess = None
		self.start = False
		self.hint_time = False
		self.starter = None
		self.word = None
		self.confirmed = None
		self.checking = False
		self.current_round = 0
		self.hint_submission = 0
		self.submitted_hints = ""

# game_data = {
# 	'members': [],
# 	'round': 13,
# 	'hints': {},
# 	'words' : open("C:/Users/byukim/Documents/python/discord_bot/Just one/word_list.txt",
#              'r', encoding='UTF-8').read().split('\n'),
# 	'already': [],
# 	'guesser': None,
# 	'main_channel': None,
# 	'guess': None,
# 	'start': False,
# 	'hint_time': False,
# 	'starter': None,
# 	'word': None,
# 	'confirmed': None,
# 	'checking': False,
# 	'current_round': 0,
# 	'hint_submission' : 0,
# 	'submitted_hints' : ""
# }