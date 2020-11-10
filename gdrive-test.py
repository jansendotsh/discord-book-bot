# toDo
# Make work in Discord bot events

import os, gspread, random
from oauth2client.service_account import ServiceAccountCredentials

def main():
    # Open the Google Sheet with book data
    gc = gspread.service_account(filename='key.json')
    sheet = gc.open_by_key("1VoR6d3Vwbhk5sxh18jUwtSZP3hr_hBjUn2CDSmBQzus")
    
    upcoming = sheet.get_worksheet(3).get_all_records()
    lengthUp = len(upcoming)
    randoBook = random.randint(2,lengthUp+1)
    newNext = sheet.get_worksheet(3).row_values(randoBook)

    print(newNext)
    print(randoBook)

    sheet.get_worksheet(3).insert_row(newNext,2)
    sheet.get_worksheet(3).delete_rows(randoBook+1)


if __name__ == '__main__':
    main()
