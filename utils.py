def find_game_of_this_channel(active_game, user_id):
    for channel_id in active_game:
        for member in active_game[channel_id].members:
            if user_id == member.id:
                return active_game[channel_id]
    return None