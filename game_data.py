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
        self.submitted = {}
        self.correct = 0
        
active_game = {}