# dumas

## Running bot

The bot needs a configuration file, which contains important data. A configuration file should look like this:

```json
{
  "botId": 123456789,
  "token": "looooong token",
  "sourceChannels": [
    123456789
  ],
  "targetChannel": 123456789,
  "messageLimit": 10000,
  "messageFrequency": 60,
  "minimumMessageLength": 9,
  "firstMessage": "hey it's a me, discord bot!"
}
```

After you created the file, pass the absolute path as a command line argument.
