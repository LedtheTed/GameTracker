import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import creds

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = ServiceAccountCredentials.from_json_keyfile_name('gs_credentials.json', scope)
client = gspread.authorize(credentials)
gc_name = 'LodtheFraud\'s Game Rankings'
gc_key = creds.gc_key
email = creds.email
header_row_index = 1

def make_sheet():
    print("-- Making new sheet --")
    print(f"- Sheet name: {gc_name}")

    sheet = client.create(gc_name)
    sheet.share(email, perm_type='user', role='writer')

def get_game_data():
    sheet = client.open_by_key(gc_key).get_worksheet(0)
    return sheet.get_all_records()

def get_column(sheet, name):
    header_row = sheet.row_values(header_row_index)
    try:
        return chr(header_row.index(name) + 1 + 64)
    except ValueError:
        print(f"Header '{name}' not found.")
        return None
    
def update_playtimes(csv_file):
    print("--- GOOGLE SHEETS ---")
    print("-- Opening sheet --")
    print(f"- Sheet name: {gc_name} -")
    print(f"- Sheet key: {gc_key} -")

    # Fetch current data from the Google Spreadsheet
    sheet = client.open_by_key(gc_key).get_worksheet(0)
    data = sheet.get_all_records()
    
    print("- Sheet opened -")
    print("- Converting to dataframe -")

    # Convert to DataFrame for easier manipulation
    sheet_df = pd.DataFrame(data)
    print("- Successfully converted -")
    print("-- Getting Steam data -- ")

    # Read the CSV file
    steam_data = pd.read_csv(csv_file, encoding='latin1')
    print("- Steam data found -")
    print("-- Updating Spreadsheet --")

    column_indices = {
        'ID': get_column(sheet, 'ID'),
        'Game': get_column(sheet, 'Game'),
        'Platform': get_column(sheet, 'Platform'),
        'Playtime (Hours)': get_column(sheet, 'Playtime (Hours)'),
        'Rating': get_column(sheet, 'Rating'),
        'Completion': get_column(sheet, 'Completion'),
        'Last Played': get_column(sheet, 'Last Played')        
    }

    updates = []

  # Update playtime and hyperlinks in the spreadsheet directly
    for index, row in steam_data.iterrows():
        game = {
            'id': row['id'],
            'name': row['name'],
            'store_link': row['store_link'],
            'playtime': row['playtime'],
            'last_played': row['last_played']
        }

        # Find the index of the game in the spreadsheet
        match = sheet_df[sheet_df['ID'] == game['id']]
        if not match.empty:
            # Get the row index for the matching game
            row_index = match.index[0] + 3  # +2 because Google Sheets is 1-indexed, +1 for the header row, and +1 for the game rec row

            # Create a hyperlink formula for Google Sheets
            hyperlink_formula = f'=HYPERLINK("{game['store_link']}", "{game['name']}")'

            # Prepare the updates for the batch request
            updates.append({
                'range': f'{column_indices['Game']}{row_index}',
                'values': [[hyperlink_formula]]
            })
            updates.append({
                'range': f'{column_indices['Playtime (Hours)']}{row_index}',
                'values': [[f"{game['playtime']}"]]
            })
            updates.append({
                'range': f'{column_indices['Last Played']}{row_index}',
                'values': [[f"{game['last_played']}"]]
            })
            updates.append({
                'range': f'{column_indices['Platform']}{row_index}',
                'values': [[f"Steam"]]
            })


    sheet.batch_update(updates, value_input_option='user_entered')

    print("-- Spreadsheet updated successfully --")
