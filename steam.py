import requests
import csv
import re
import datetime
import creds

key = creds.key
steam_id = creds.steam_id

manual_games = [
    [690040, "SUPERHOT: MIND CONTROL DELETE"],
    [570460, "Laser League: World Arena"],
    [701160, "Kingdom Two Crowns"],
    [739630, "Phasmophobia"],
    [753420, "Dungreed"],
    [753640, "Outer Wilds"],
    [1399780, "Spellbreak"],
    [1664200, "Duelists of Eden"],
    [1782210, "Crab Game"],
    [1874490, "Potionomics"],
    [1966720, "Lethal Company"]
    ]



def get_steam_game_list():
    print("-- Getting list of steam games --")
    url = "http://api.steampowered.com/ISteamApps/GetAppList/v2/"
    response = requests.get(url)
    data = response.json()
    all_game_list = {game['appid']: game['name'] for game in data['applist']['apps']}
    
    for game in manual_games:
        all_game_list[game[0]] = game[1]
        
    return all_game_list


def get_game_data(api_key, steam_id, all_game_list):
    print("-- Getting game data --")
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&format=json"
    response = requests.get(url)
    data = response.json()
    cleaned_games = []
    for full_game in data['response']['games']:

        try:
            last_played = full_game['rtime_last_played']
        except:
            last_played = ('Error')

        game = {
            'id': full_game['appid'], 
            'playtime': full_game['playtime_forever'],
            'last_played': last_played
            }
        if game['playtime'] <= 60:
            continue

        # Find name of game
        try:
            name = all_game_list[game['id']]
            game['name'] = remove_non_ascii(name)
        except KeyError:
            try:
                error_url = "https://store.steampowered.com/api/appdetails?appids=" + str(game['id'])
                error_response = requests.get(error_url)
                error_data = error_response.json()
                error_game_data = error_data[str(game['id'])]
                error_game = error_game_data['data']
                name = error_game['name']

                game['name'] = remove_non_ascii(name)
                print(f"-- + App {game['id']} name found: " + name + " --")
            except KeyError:
                print(f"-- X App {game['id']} name not found --")

        if game['last_played'] and game['last_played'] != 'Error':
            game['last_played'] = datetime.date.fromtimestamp(game['last_played']).strftime('%m-%d-%Y')
        else:
            game['last_played'] = 'Error'
        
        game['playtime'] = (game['playtime'] // 6) / 10
        game['store_link'] = f"https://store.steampowered.com/app/{game['id']}/"
        cleaned_games.append(game)


    return cleaned_games

def make_game_data_file(file_name):
    print("--- STEAM DATA ---")
    print(f"- Filename: {file_name} -")
    all_game_list = get_steam_game_list()
    games = get_game_data(key, steam_id, all_game_list)
    games = sorted(games, key=lambda x: x['playtime'], reverse=True)

    with open(file_name, 'w', newline='') as f:
        writer = csv.DictWriter(f,fieldnames=['id', 'name', 'playtime', 'store_link', 'last_played'])
        writer.writeheader()
        for game in games:
            writer.writerow(game)
    print("--- STEAM DATA COMPLETE ---")
    print()

def remove_non_ascii(text):
    return re.sub(r'[^\x00-\x7F]', '', text)