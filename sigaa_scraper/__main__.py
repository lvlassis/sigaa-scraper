import sys
import json
import inspect
import dataclasses

import sigaa_scraper as _pkg
from sigaa_scraper import SessionExpiredError, UnexpectedPageError


def _discover_commands():
    commands = {}
    for name, cls in inspect.getmembers(_pkg, inspect.isclass):
        if not name.endswith("Scraper"):
            continue
        for method_name in dir(cls):
            if method_name.startswith("get_") and callable(getattr(cls, method_name)):
                key = method_name.removeprefix("get_")
                commands[key] = (cls, method_name)
    return commands


def _serialize(result):
    if dataclasses.is_dataclass(result) and not isinstance(result, type):
        return dataclasses.asdict(result)
    if isinstance(result, list):
        return [dataclasses.asdict(i) if (dataclasses.is_dataclass(i) and not isinstance(i, type)) else i for i in result]
    return result


def main():
    cookies = sys.stdin.read().strip()
    commands = _discover_commands()

    if len(sys.argv) < 2:
        if len(commands) == 1:
            page = next(iter(commands))
        else:
            print(
                json.dumps({"error": "page_required", "available": sorted(commands)}),
                file=sys.stderr,
            )
            sys.exit(3)
    else:
        page = sys.argv[1]

    if page not in commands:
        print(
            json.dumps({"error": "unknown_page", "available": sorted(commands)}),
            file=sys.stderr,
        )
        sys.exit(3)

    cls, method_name = commands[page]
    try:
        result = getattr(cls(cookies), method_name)()
        print(json.dumps(_serialize(result)))
    except SessionExpiredError:
        print(json.dumps({"error": "session_expired"}), file=sys.stderr)
        sys.exit(1)
    except UnexpectedPageError:
        print(json.dumps({"error": "unexpected_page"}), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
