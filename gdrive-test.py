# toDo
# Make work in Discord bot events

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def main():
    # Open the Google Sheet with book data
    gc = gspread.service_account(filename='key.json')
    sheet = gc.open_by_key("1VoR6d3Vwbhk5sxh18jUwtSZP3hr_hBjUn2CDSmBQzus")

    def progress(username, progress):
        progSheet = sheet.get_worksheet(3)
        pageCount = int(progSheet.cell(1, 3).value)

        try:
            curEntry = progSheet.find(username)
            progCell = curEntry.col + 1

            if progress[-1] == "%":
                progSheet.update_cell(curEntry.row, progCell, progress)
            else:
                progress = int(progress)
                progress = str(int((progress/pageCount)*100))
                progSheet.update_cell(curEntry.row, progCell, progress+"%")

        except gspread.exceptions.CellNotFound:
            progSheet.append_row([username, progress])

    progress("frailtyy#7182","222")

if __name__ == '__main__':
    main()