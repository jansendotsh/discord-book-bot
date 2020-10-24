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
        curIndex = len(current) - 1
        print("The current book is {} by {}. Information about this book is available here:\nGoodreads Link: {}\n\nThey can be downloaded at:\neBook Link: {}\nAudiobook Link: {}".format(current[curIndex]['Title'],current[curIndex]['Author'],current[curIndex]['Goodreads Link'],current[curIndex]['eBook Link'],current[curIndex]['Audiobook Link']))

    # Past books
    def pastBooks(length):
        past = sheet.get_worksheet(1).get_all_records()

        if type(length) == int:                
            if len(past) >= length:
                print("These were the most recent books from outer space:")
                for i in range(len(past)-1,(len(past)-length-1),-1):
                    # This iterates backwards against the length variable 
                    print("{} by {}".format(past[i]['Title'],past[i]['Author']))
            else:
                for i in range((len(past)-1),-1,-1):
                    # When number is higher than value, it'll just print the value
                    print("{} by {}".format(past[i]['Title'],past[i]['Author']))
        else:
            return("Not a valid length. Please use a number.")

    # Next book on Current/Upcoming list
    def nextBook():
        upcoming = sheet.get_worksheet(0).get_all_records()
        print("The next book is {} by {}. If this is incorrect, review the spreadsheet here: https://jnsn.link/bookclub".format(upcoming[0]['Title'],upcoming[0]['Author']))

    def addBook(title,author):
        indexLen = len(sheet.get_worksheet(0).get_all_records())
        sheet.get_worksheet(0).append_row([title, author])
        print("Book added! Verify here: https://jnsn.link/bookclub")

if __name__ == '__main__':
    main()