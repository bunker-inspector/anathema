# anathema
Dice roller for tabletop games with some specific leanings towards Pathfinder 2e.

[![anathema](https://circleci.com/gh/bunker-inspector/anathema.svg?style=svg)](https://app.circleci.com/pipelines/github/bunker-inspector/anathema)

Make sure you have RocksDB installed wherever you plan to run this and isntall everything else from `requirements.txt`. Set the `DISCORD_BOT_TOKEN` with your bot's access token and run from the entrypoint at `src/anathema.py`

Maybe I should make a copywrite disclaimer about Sun Tzu's _The Art of War_ but I imagine it's in public domain by now? If you are a lawyer, feel free to open an issue I suppose.

Generally follows the same syntax as Dice Maiden
`!roll [DIE_EXPR|MOD_EXPR] [+|-] DIE_EXPR|MOD_EXPR] ...  [XFORM_EXPR] ! <reason>`
Where: 
`DIE_EXPR` is `XdX`, e.g. `1d20`,`2d6`
`MOD_EXPR` is `X`, e.g. `1`, `8`

`XFORM_EXPR` are currently:
`khX`: "Keep highest X", will take the top X rolls from each `DIE_EXPR` result
`klX`: "Keep lowest X", will take the bottom X rolls from each `DIE_EXPR` result

`reason` can be any text which explains the result in the response

Full example:
`!roll 2d6 + 1d8 +4 -1 kh1 ! attack vs goblin AC`

Additionally, some simple "macros" are supported with the syntax:
`!set-command <command_name> :: <command_expression>`

Where the 'command expression` is anything that could be valid to another handler. Optionally you can add a `{}` to allow some text to be injected into the command when you call it.

For example:
`!set-command attack :: !roll 1d20 + 8 {} ! attack`

and then

`!attack -2` , which will expand to: `!set-command attack :: !roll 1d20 + 8 -2 ! attack`
