import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Iterable


def ensure_sys_path(paths: Iterable[Path]) -> None:
    for path in paths:
        text = str(path)
        if text not in sys.path:
            sys.path.insert(0, text)


def load_module(name: str, path: Path, clear_modules: Iterable[str] | None = None):
    if clear_modules:
        for module_name in clear_modules:
            sys.modules.pop(module_name, None)

    sys.modules.pop(name, None)

    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module

    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def load_event(events_dir: Path, name: str) -> dict:
    return json.loads((events_dir / name).read_text(encoding="utf-8"))


def find_backend_root(start_path: Path) -> Path:
    for candidate in (start_path.resolve(), *start_path.resolve().parents):
        if candidate.name == "backend":
            return candidate
    raise RuntimeError(f"Unable to locate backend root from {start_path}")
