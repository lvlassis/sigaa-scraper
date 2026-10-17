import sys
import json
import inspect
import dataclasses

import sigaa_scraper as _pkg
from sigaa_scraper import NetworkError, SessionExpiredError, UnexpectedPageError


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
    if sys.stdin.isatty():
        print(
            json.dumps({"error": "cookies_required", "hint": "Forneca o cookie via stdin: echo 'SEU_COOKIE' | sigaa-scraper"}),
            file=sys.stderr,
        )
        sys.exit(3)

    cookies = sys.stdin.read().strip()
    if not cookies:
        print(json.dumps({"error": "cookies_required"}), file=sys.stderr)
        sys.exit(3)

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
    except NetworkError as e:
        print(json.dumps({"error": "network_error", "detail": str(e)}), file=sys.stderr)
        sys.exit(4)


if __name__ == "__main__":
    main()
