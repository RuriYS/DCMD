import json
import glob
import re
import time
from collections import defaultdict


def main():
    # Load configuration and channel index
    config = load_config()
    channel_index = load_channel_index()

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

        # Check channel whitelist/blacklist
        if not filter_by_list(channel_id, config["channels"]):
            continue

        # Check guild filtering
        guild_name = get_guild_name(channel_index.get(channel_id))
        if guild_name:
            # Skip if it's a DM and ignore_dms is True
            if guild_name == "DM" and config.get("ignore_dms", False):
                continue
            # Check guild whitelist/blacklist
            if not filter_by_list(guild_name, config["guilds"]):
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


def load_channel_index():
    try:
        with open("messages/index.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: index.json not found in messages directory")
        return {}


def filter_by_list(item, config_section):
    """Helper function to handle whitelist/blacklist logic"""
    if config_section["whitelist"]:
        return item in config_section["whitelist"]
    if config_section["blacklist"]:
        return item not in config_section["blacklist"]
    return True


def get_guild_name(channel_info):
    if not channel_info:
        return None

    # Check if it's a DM
    if channel_info.startswith("Direct Message"):
        return "DM"

    # Try to extract guild name
    match = re.search(r"(?:Unknown channel in |.* in )(.+)$", channel_info)
    if match:
        return match.group(1)

    return None


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

    # Filter words
    if config["filters"]["words"]:
        if any(word in msg for word in config["filtered_words"]):
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


def save_messages(messages, config):
    if "json" in config["output"]:
        channel_index = load_channel_index()
        formatted_output = []

        for channel_id, msgs in messages.items():
            channel_info = channel_index.get(channel_id, "Unknown Channel")
            guild_name = get_guild_name(channel_info) or "Unknown Guild"
            channel_name = (
                channel_info.split(" in ")[0]
                if " in " in channel_info
                else channel_info
            )

            formatted_output.append(
                {
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "guild_name": guild_name,
                    "messages": sorted(msgs),
                }
            )

        with open("dump.json", "w+", encoding="utf-8") as f:
            json.dump(formatted_output, f, ensure_ascii=False, indent=2)
        print("Saved to dump.json")

    if "txt" in config["output"]:
        with open("dump.txt", "w+", encoding="utf-8") as f:
            for channel_messages in messages.values():
                for msg in sorted(channel_messages):
                    f.write(f"{msg}\n")
        print("Saved to dump.txt")


if __name__ == "__main__":
    messages = main()
    save_messages(messages, load_config())
    total_messages = sum(len(msgs) for msgs in messages.values())
    print(f"{total_messages} messages dumped across {len(messages)} channels")
