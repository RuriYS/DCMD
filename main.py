import json
import glob
import re
import time

## Globals
messages_path = "messages"
filter_links = False  # Remove messages with URLs
filter_emojis = False  # Remove messages with emojis
filter_commands = False  # Remove messages starting with $, %, !, ., #
filter_symbols = False  # Remove messages containing special symbols
filter_multilines = False  # Remove messages with multiple lines
filter_duplicates = False  # Remove duplicate messages
filter_numbers = False  # Remove messages containing only numbers
min_length = 1  # Min message length; None if infinite
max_length = None  # Max message length; None if infinite
limit = None  # Max messages to dump; None if infinite
command_prefixes = ["$", "%", "!", ".", "#"]
symbols = ["\n", "**", "<@", "<#", "`", "://"]
messages = []


def main():
    start = time.time()
    seen_messages = dict.fromkeys([]) if filter_duplicates else None

    for file in glob.glob(f"{messages_path}/**/messages.json", recursive=True):
        with open(file, "r") as f:
            _messages = json.load(f)
            contents = list(map(lambda d: d["Contents"].strip(), _messages))

            if filter_duplicates:
                new_contents = []
                for content in contents:
                    if content not in seen_messages:
                        seen_messages[content] = None
                        new_contents.append(content)
                contents = new_contents

            contents = list(filter(filter_message, contents))
            contents = list(map(clean_message, contents))

            if len(contents) <= 0:
                continue

            for content in contents:
                if limit and len(messages) >= limit:
                    break
                messages.append(content)
    print(f"Took {round(time.time() - start, 2)} seconds")


def filter_message(msg: str):
    # Check message length
    word_count = len(msg.split())
    if word_count < min_length:
        return False
    if max_length and word_count >= max_length:
        return False

    # Filter command prefixes
    if filter_commands:
        if any(msg.startswith(prefix) for prefix in command_prefixes):
            return False

    # Filter links
    if filter_links:
        if re.search(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            msg,
        ):
            return False

    # Filter emojis
    if filter_emojis:
        if re.search(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
            msg,
        ):
            return False

    # Filter symbols
    if filter_symbols:
        if any(symbol in msg for symbol in symbols):
            return False

    # Filter multilines
    if filter_multilines:
        if len(msg.split("\n")) > 1:
            return False

    # Filter numbers
    if filter_numbers:
        if msg.isdigit():
            return False

    return True


def clean_message(msg):
    # Remove URLs if filter_links is True
    if filter_links:
        msg = re.sub(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            "",
            msg,
        )

    # Remove emojis and special unicode if filter_emojis is True
    if filter_emojis:
        msg = re.sub(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
            "",
            msg,
        )
    return msg


if __name__ == "__main__":
    main()
    with open("dump.json", "w+", encoding="utf-8") as f:
        json.dump(sorted(messages), f, ensure_ascii=False, indent=2)

    print(f"{len(messages)} messages dumped")
