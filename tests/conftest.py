from pathlib import Path

import pytest
import yaml

_PAGES_DIR = Path(__file__).parent / "pages"


def page_vectors():
    pairs = []
    for html_path in sorted(_PAGES_DIR.glob("*.html")):
        yaml_path = html_path.with_suffix(".yaml")
        if yaml_path.exists():
            html = html_path.read_text(encoding="utf-8")
            expected = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            pairs.append(pytest.param(html, expected, id=html_path.stem))
    return pairs
