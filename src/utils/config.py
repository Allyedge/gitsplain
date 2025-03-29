import os
import sys
import configparser


def get_api_key_from_config() -> str | None:
    config_path = os.path.expanduser("~/.config/gitsplain/config")
    if not os.path.exists(config_path):
        return None
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        return config.get("gitsplain", "api_key", fallback=None)
    except Exception:
        print(f"WARNING: Could not read config file {config_path}.", file=sys.stderr)
        return None


def set_api_key_in_config(api_key: str) -> bool:
    config_dir = os.path.expanduser("~/.config/gitsplain")
    config_path = os.path.join(config_dir, "config")

    try:
        os.makedirs(config_dir, exist_ok=True)

        config = configparser.ConfigParser()

        if os.path.exists(config_path):
            config.read(config_path)

        if not config.has_section("openai"):
            config.add_section("openai")

        config.set("openai", "api_key", api_key)

        with open(config_path, "w") as configfile:
            config.write(configfile)

        print(f"API key successfully stored in {config_path}", file=sys.stderr)
        return True

    except OSError as e:
        print(f"ERROR: Failed to write config file {config_path}: {e}", file=sys.stderr)
        return False
    except configparser.Error as e:
        print(f"ERROR: Failed to parse config file {config_path}: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}", file=sys.stderr)
        return False
