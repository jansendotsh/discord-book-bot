# Discord Book Bot

## Goal

This is a bot that is intended to function as a tool for a book club channel in Discord. The bot will connect to a data source hosted in Google Sheets acting as a lightweight database. 

## Requirements

- Python 3
- Py3 Modules:
	- virtualenv (recommended)
	- discord.py
	- gspread

## Usage

In Python directly:
```
source ./bin/activate
pip install -r requirements
python book-bot.py
```

In Docker:
```
docker build -t book-bot:0.1
docker run -v $(pwd)/key.json:/usr/src/app/key.json -e DISCORD_TOKEN='<DISCORD-BOT-TOKEN>' --rm book-bot:0.1
```

## Goals

- Add book commands
- docker-compose
