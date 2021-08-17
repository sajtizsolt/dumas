# dumas

A Discord bot written in Python to bring back memories and create funny conversations for you and your friends.

## What is it?

This program will let a Discord bot read your old messages and randomly send them to a specified channel. If you and your friends talk a lot, some of your messages taken out of context will entertain you, we promise!

## Installation

### Dependencies

Since the bot is written in Python, you only need to install a Python environment some dependencies with `pip`, using the following command:

```bash
$ pip install discord.py
```
### Configuration

The program needs a configuration file, which contains important data about your server and bot. The configuration file should look like this:

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

| Field             | Type           | Description                                             |
| ----------------- | -------------- | ------------------------------------------------------- |
| `bot.app`           | `integer`        | ID of the application which owns the bot                |
| `bot.token`         | `string`         | secret token of the bot                                 |
| `channel.sources`   | `array[integer]` | IDs of the channels of which the bot will _pick_ messages |
| `channel.target`    | `integer`        | ID of the channels to which the bot will _send_ messages  |
| `message.farewell`  | `string`         | the message the bot will send before disconnecting      |
| `message.frequency` | `integer`        | the frequency of the continous messages (in seconds)    |
| `message.length`    | `integer`        | the minimum length of the messages to choose from       |
| `message.limit`     | `integer`        | the maximum number of messages to parse                 |
| `message.welcome`   | `string`         | the message the bot will send after connecting          |

## How to run

After you installed the dependencies and created a configuration file, you can simply run the program with the following command:

```bash
$ python main.py <absolute-path-to-configuration-file>
```

## Commands

As every good bot, `dumas` also has commands. Just type one of these into a channel, which has been specified as source.

| Command   | Description                                                                                |
| --------- | ------------------------------------------------------------------------------------------ |
| `&help`   | `dumas` will show how to use it                                                            |
| `&start`  | `dumas` will send a message from time to time (based on the value of `message.frequency`)  |
| `&stop`   | `dumas` will stop sending messages                                                         |
| `&random` | `dumas` will send a random message immediately                                             |

## Deploying to Heroku

Maybe, you will want to deploy your bot to `Heroku`. You can find many great guides on the internet, to deploy an application, but I want to share some important information about this application.

After you deployed `dumas`, the program will search for the specified configuration file every minute, until finds it. However, the `Heroku` deploy process won't create a config file for you - you will have to create it manually. To achive your goal, you will need `heroku-cli`.

With the help of the following commands, you will be able to create a configuration file in minutes:

```bash
$ heroku run bash --app <app-name>
$ touch config
$ echo "{\"bot\":{...}}" > config
$ exit
```

If you will run the program in `Heroku`, it will search for the configuration file at `/app/config`, so be careful where you put your file.

### Useful commands

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

To check if dynos ar running use the following commands:

```bash
$ heroku ps --app <app-name>
```
