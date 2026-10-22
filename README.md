# dumas

A Discord bot written in Python to bring back memories and create funny conversations for you and your friends.

## What is it?

This program will let a Discord bot read your old messages and randomly send them to a specified channel. If you and your friends talk a lot, some of your messages taken out of context will entertain you, we promise!

## Installation

### Dependencies

Install dependencies using `uv`:

```bash
$ uv sync
```

> [!IMPORTANT]
> Since Dumas reads message history, make sure to enable the **Message Content Intent** in your [Discord Developer Portal](https://discord.com/developers/applications) under your bot's **Bot** settings tab.

### Configuration

The program needs a configuration file, which contains important data about your server and bot. You can also provide the bot token via the `DISCORD_TOKEN` environment variable or `.env` file instead of storing it in plaintext. The configuration file should look like this:

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
    "warning": "Oh, I see what you did there!",
    "welcome": "It's a me, Discord bot!"
  }
}
```

| Field               | Type             | Description                                                    |
| ------------------- | ---------------- | -------------------------------------------------------------- |
| `bot.app`           | `integer`        | ID of the application which owns the bot                       |
| `bot.token`         | `string`         | secret token of the bot                                        |
| `channel.sources`   | `array[integer]` | IDs of the channels from which the bot will _pick_ messages    |
| `channel.target`    | `integer`        | ID of the channel to which the bot will _send_ messages        |
| `message.farewell`  | `string`         | the message the bot will send before disconnecting             |
| `message.frequency` | `integer`        | the frequency of continuous messages (in seconds)              |
| `message.length`    | `integer`        | the minimum length of the messages to choose from              |
| `message.limit`     | `integer`        | the maximum number of messages to parse                        |
| `message.warning`   | `string`         | the message the bot will send when an expected problem occurs  |
| `message.welcome`   | `string`         | the message the bot will send after connecting                 |

## How to run

After installing dependencies and creating a configuration file, run Dumas:

```bash
$ uv run dumas [options] <path-to-configuration-file>
```

You can also set the configuration path via the `DUMAS_CONFIG` environment variable or in a `.env` file, allowing you to run:

```bash
$ uv run dumas
```

## Development & Testing

Run tests and code quality checks using `uv`:

```bash
# Run unit tests
$ uv run pytest

# Lint and check formatting
$ uv run ruff check .
$ uv run ruff format --check .

# Type checking
$ uv run mypy src/ tests/
```

## Commands

As every good bot, `dumas` also has commands. Just type one of these into a channel, which has been specified as source.

| Command               | Description                                                                               |
| --------------------- | ----------------------------------------------------------------------------------------- |
| `&help`               | `dumas` will show how to use it                                                           |
| `&start [author_id]`  | `dumas` will send a message from time to time (based on the value of `message.frequency`) |
| `&stop`               | `dumas` will stop sending messages                                                        |
| `&random [author_id]` | `dumas` will send a random message immediately                                            |
| `&show-config`        | `dumas` will show the active configuration (alias: `&get-config`)                          |

