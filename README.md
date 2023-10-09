# reddit-live-bot

A script to monitor Reddit Live event threads and send updates using webhooks.

Intended to be sent to Discord & Slack webhook URLs.

Refreshed every 2 minutes (Default), this can be configured in `conf.yaml`

## Requirements

- Python 3.6+
- Packages per `requirements.txt`

## Running

1. `pip install -r requirements.txt`
2. Create your own `conf.yaml` file from the sample and set [Discord](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) or [Slack](https://api.slack.com/messaging/webhooks) webhook URL
3. `python live.py`

🇺🇦