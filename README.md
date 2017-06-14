soladm
------

![](reinhard.jpg)

CLI Soldat Admin Client - control those pesky players.

## Features

- Logging to file
- Autocompletion
    - Commands
    - Player names
    - Map names (context-sensitive, after `/map`)
    - Bot names (context-sensitive, after `/addbot`)
- Automatic reconnecting
- Configuration via .INI files
- Command history
- libreadline/"bash" shortcuts in the input field
- Filtering by regex
- Showing old logs after restart (up to *n* lines)
- Bell on regex (can be used for notifications via window decorations like in WeeChat and irssi)
- Configurable colors, color schemes (built-in scheme for dark and light terminals)

#### To do

- Ability to connect to different server or with different password

## Non-features

- No Soldat TV: might add ASCII art renderer, when all other features are finished
- No multiple connections: use terminal multiplexer such as `tmux` or `screen`.

## Usage

```
$ git clone https://github.com/rr-/soladm
$ cd soladm
$ pip install --user --upgrade .
$ soladm --help
```

#### Config file

For structure of the .INI file please refer to the [default configuration
file](soladm/data/default_config.ini).

## Keyboard shortcuts

Key                             | Action
---                             | ---
<kbd>ctrl q</kbd>               | quit
<kbd>ctrl c</kbd>               | quit
<kbd>ctrl p</kbd>, <kbd>↑</kbd> | previous command
<kbd>ctrl n</kbd>, <kbd>↓</kbd> | next command
<kbd>tab</kbd>                  | cycle autocomplete
<kbd>shift tab</kbd>            | cycle autocomplete (reverse direction)
<kbd>page up</kbd>              | scroll console up by one page
<kbd>page down</kbd>            | scroll console down by one page
<kbd>ctrl l</kbd>               | clear console

## Keyboard shortcuts (readline compatibility)

Key                                          | Action
---                                          | ---
<kbd>ctrl a</kbd>, <kbd>home</kbd>           | navigate to the start of the line
<kbd>ctrl e</kbd>, <kbd>end</kbd>            | navigate to the end of the line
<kbd>ctrl b</kbd>, <kbd>←</kbd>              | navigate a single character back
<kbd>ctrl f</kbd>, <kbd>→</kbd>              | navigate a single character forward
<kbd>meta b</kbd>, <kbd>shift ←</kbd>        | navigate a single word back
<kbd>meta f</kbd>, <kbd>shift →</kbd>        | navigate a single word forward
<kbd>ctrl d</kbd>, <kbd>delete</kbd>         | delete a single character after cursor
<kbd>ctrl h</kbd>, <kbd>backspace</kbd>      | delete a single character before cursor
<kbd>meta d</kbd>                            | delete a single word after cursor
<kbd>ctrl w</kbd>, <kbd>meta backspace</kbd> | delete a single word before cursor
<kbd>ctrl u</kbd>                            | delete whole line
<kbd>ctrl k</kbd>                            | delete everything after cursor
<kbd>ctrl t</kbd>                            | transpose last 2 characters before cursor
