# dumas

A Discord bot written in Python to bring back memories and create funny conversations for you and your friends.

## Installation

Since the bot is written in Python, you only need to install a Python environment some dependencies with `pip`, using the following command:

```bash
$ pip install discord.py
```

### Configuration




## Commands

As every good bot, `dumas` also has commands.

| Command   | Description                                                                                |
| --------- | ------------------------------------------------------------------------------------------ |
| `&help`   | `dumas` will show how to use it                                                            |
| `&start`  | `dumas` will send a message from time to time (based on the value of `message.frequency`)  |
| `&stop`   | `dumas` will stop sending messages                                                         |
| `&random` | `dumas` will send a random message immediately                                             |

## Running bot

The bot needs a configuration file, which contains important data. A configuration file should look like this:

```json
{
  "bot": {
    "app": 123456789987654321,
    "token": "AbcDeFGhIjKLMnoPqRStUvWXYz123-4.5_6789abCdEFGhiYKlMnJoP-rsT"
  },
  "channel": {
    "sources": [
      123456789987654321
    ],
    "target": 123456789987654321
  },
  "message": {
    "farewell": "Goodbye friends!",
    "frequency": 5,
    "length": 10,
    "limit": 1000,
    "welcome": "It's a me, Discord bot!"
  }
}
```

After you created the file, pass the absolute path as a command line argument.

## Heroku

To completely stop the application use the following commands:

```bash
$ heroku maintenance:on --app <app-name>
$ heroku ps:scale web=0 --app <app-name>
```

To turn on later use the following commands:

```bash
$ heroku maintenance:off --app <app-name>
$ heroku ps:scale web=1  --app <app-name>
```
