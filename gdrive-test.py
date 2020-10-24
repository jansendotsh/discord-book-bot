# toDo
# Make work in Discord bot events

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def main():
    # Open the Google Sheet with book data
    gc = gspread.service_account(filename='key.json')
    sheet = gc.open_by_key("1VoR6d3Vwbhk5sxh18jUwtSZP3hr_hBjUn2CDSmBQzus")

    # Current Book
    def currentBook():
        current = sheet.get_worksheet(1).get_all_records()
        print("The current book is {} by {}. Information about this book is available here:\nGoodreads Link: {}\n\nThey can be downloaded at:\neBook Link: {}\nAudiobook Link: {}".format(current[0]['Title'],current[0]['Author'],current[0]['Goodreads Link'],current[0]['eBook Link'],current[0]['Audiobook Link']))

    # Past books
    def pastBooks(length):
        past = sheet.get_worksheet(1).get_all_records()
        print(past[0])
        if type(length) == int:                
            if len(past) >= length:
                print("These were the most recent books from outer space:")
                for i in range(0,length,1):
                    print("{} by {}".format(past[i]['Title'],past[i]['Author']))
            else:
                for i in range(0,len(past),1):
                    print("{} by {}".format(past[i]['Title'],past[i]['Author']))
        else:
            return("Not a valid length. Please use a number.")

    # Next book on Current/Upcoming list
    def nextBook():
        upcoming = sheet.get_worksheet(0).get_all_records()
        print("The next book is {} by {}. If this is incorrect, review the spreadsheet and call a vote: https://jnsn.link/bookclub".format(upcoming[0]['Title'],upcoming[0]['Author']))

    # Adding a new book
    def addBook(title,author):
        indexLen = len(sheet.get_worksheet(0).get_all_records())
        sheet.get_worksheet(0).append_row([title, author])
        print("Book added! Verify here: https://jnsn.link/bookclub")

    def swapBook():
        nextUp = sheet.get_worksheet(0).row_values(2)
        sheet.get_worksheet(1).insert_row(nextUp,2)
        indexLen = len(sheet.get_worksheet(0).get_all_records())
        sheet.get_worksheet(0).delete_row(2)
        print("New book has been started...\n")
        currentBook()

if __name__ == '__main__':
    main()