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
docker build -t book-bot:latest
docker run -v $(pwd)/key.json:/usr/src/app/key.json -e DISCORD_TOKEN='<DISCORD-BOT-TOKEN>' --rm book-bot:latest
```

Deploying Docker image via Ansible:
```
ansible-playbook deploy.yml -K -i <host-address>, -e ansible_python_interpreter=/usr/bin/python3 --ssh-common-args "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
```

## Goals

- (Optional) update thumbnails on search responses 
	- would need to dump clear fields and re-write embed each time (kinda sucks)
- Add progress/update system
- Adding ebook/audiobook links 
- sample/starter db
- backup db script for cron/s3