import json
import glob
import re
import time
from collections import defaultdict


def main():
    config = load_config()

    # Initialize message storage
    messages = defaultdict(list)
    start = time.time()
    seen_messages = dict.fromkeys([]) if config["filters"]["duplicates"] else None

    for file in glob.glob(
        f"{config['messages_path']}/**/messages.json", recursive=True
    ):
        channel_id = re.search(r"messages/c(\d+)/messages\.json", file)
        if not channel_id:
            continue

        channel_id = channel_id.group(1)
        if channel_id in config["ignored_channels"]:
            continue

        with open(file, "r") as f:
            _messages = json.load(f)
            contents = list(map(lambda d: d["Contents"].strip(), _messages))

            if config["filters"]["duplicates"]:
                new_contents = []
                for content in contents:
                    if content not in seen_messages:
                        seen_messages[content] = None
                        new_contents.append(content)
                contents = new_contents

            contents = list(filter(lambda msg: filter_message(msg, config), contents))
            contents = list(map(lambda msg: clean_message(msg, config), contents))

            if len(contents) <= 0:
                continue

            for content in contents:
                if (
                    config["limit"]
                    and sum(len(msgs) for msgs in messages.values()) >= config["limit"]
                ):
                    break
                messages[channel_id].append(content)

    print(f"Took {round(time.time() - start, 2)} seconds")
    return messages


def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


def filter_message(msg: str, config):
    # Check message length
    word_count = len(msg.split())
    if word_count < config["length"]["min"]:
        return False
    if config["length"]["max"] and word_count >= config["length"]["max"]:
        return False

    # Filter command prefixes
    if config["filters"]["commands"]:
        if any(msg.startswith(prefix) for prefix in config["command_prefixes"]):
            return False

    # Filter links
    if config["filters"]["links"]:
        if re.search(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            msg,
        ):
            return False

    # Filter emojis
    if config["filters"]["emojis"]:
        if re.search(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
            msg,
        ):
            return False

    # Filter symbols
    if config["filters"]["symbols"]:
        if any(symbol in msg for symbol in config["symbols"]):
            return False

    # Filter multilines
    if config["filters"]["multilines"]:
        if len(msg.split("\n")) > 1:
            return False

    # Filter numbers
    if config["filters"]["numbers"]:
        if msg.strip().replace(".", "").isdigit():
            return False

    return True


def clean_message(msg, config):
    # Remove URLs if filter_links is True
    if config["filters"]["links"]:
        msg = re.sub(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            "",
            msg,
        )

    # Remove emojis and special unicode if filter_emojis is True
    if config["filters"]["emojis"]:
        msg = re.sub(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
            "",
            msg,
        )
    return msg


if __name__ == "__main__":
    messages = main()
    with open("dump.json", "w+", encoding="utf-8") as f:
        output = {k: sorted(v) for k, v in messages.items()}
        json.dump(output, f, ensure_ascii=False, indent=2)

    total_messages = sum(len(msgs) for msgs in messages.values())
    print(f"{total_messages} messages dumped across {len(messages)} channels")
