# DCMD

Discord Messages Dumper

## What is this?
It's a simple script to dump all your messages from Discord into a plain JSON.

## Data Preperation
1. Go to Privacy & Safety on your Discord's user settings.

    ![img](images/user-settings.png)

2. Scroll all the way down and find the blue "**Request Data**" button and click it.
  
    ![img](images/request-data.png)

3. Wait for a few days until you receive `package.zip` from Discord in your email (it takes a very long time, depending on how many messages you've sent, selecting more fields will take it even longer)

## Usage

1. Download this repository and extract it or run `git clone https://github.com/RuriYS/DCMD.git`
1. Download `package.zip` if you haven't already from the email Discord sent 
1. Copy `messages` folder into `DCMC`
1. Run the script:

```bash
python main.py
```
3. Filtered messages will be saved to `dump.json`

## Configuring Filters

Configure filters at the top of `main.py`:

```python
filter_links = False       # Remove messages with URLs
filter_emojis = False      # Remove messages with emojis
filter_commands = False    # Remove messages starting with $, %, !, ., #
filter_symbols = False     # Remove messages containing special symbols
filter_multilines = False  # Remove messages with multiple lines
filter_duplicates = False  # Remove duplicate messages
filter_numbers = False     # Remove messages containing only numbers
```

### Other Settings

```python
min_length = 1            # Minimum token count
max_length = None         # Maximum token count (None for unlimited)
limit = None              # Maximum messages to dump (None for unlimited)
```
