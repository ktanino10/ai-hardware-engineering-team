"""Load checked local bytes in a fresh namespace, never a cached bare import."""
import hashlib
from pathlib import Path
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parent
CODE_HASHES = {
    "sequencer.py": "634e1891186e73f46407b5037bfda7ebb84b93211b1055898e5b6be040aea745",
    "scenarios.py": "ee8028095f757ca63e1c35e07f197e7556eee0ad7734dfc37dd0afa121f24f86",
}


def load():
    sources = {}
    for filename, expected in CODE_HASHES.items():
        path = ROOT / filename
        if path.is_symlink():
            raise RuntimeError("PUBLIC_CODE_SYMLINK:" + filename)
        try:
            data = path.read_bytes()
        except OSError:
            raise RuntimeError("PUBLIC_CODE_UNREADABLE:" + filename) from None
        if hashlib.sha256(data).hexdigest() != expected:
            raise RuntimeError("PUBLIC_CODE_MISMATCH:" + filename)
        sources[filename] = data

    package = ModuleType("_rev5_public_bundle")
    prefix = "_rev5_public_bundle_" + format(id(package), "x")
    if any(name == prefix or name.startswith(prefix + ".") for name in sys.modules):
        raise RuntimeError("PUBLIC_PACKAGE_MODULE_COLLISION")
    package.__name__ = package.__package__ = prefix
    package.__path__ = []  # No filesystem search for unbound sibling modules.
    sys.modules[prefix] = package
    loaded = {}
    try:
        for filename, data in sources.items():
            short = filename.removesuffix(".py")
            name = prefix + "." + short
            module = ModuleType(name)
            module.__file__ = str(ROOT / filename)
            module.__package__ = prefix
            sys.modules[name] = module
            exec(compile(data, filename, "exec"), module.__dict__)
            setattr(package, short, module)
            loaded[short] = module
    except BaseException:
        for name in tuple(sys.modules):
            if name == prefix or name.startswith(prefix + "."):
                del sys.modules[name]
        raise
    return loaded
