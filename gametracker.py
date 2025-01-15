import steam
import sheets

# game_data_file_name = 'steam_data.csv'
game_data_file_name = 'steam_data.csv'


print()
print("----- GAME TRACKER -----")
steam.get_steam_game_list()
steam.make_game_data_file(game_data_file_name)
sheets.update_playtimes(game_data_file_name)