import importlib
import sys


REQUIRED_FUNCTIONS = {
    "database": ["init_db", "load_tracks", "upsert_track"],
    "worker": ["start_worker"],
}


def validate_imports():
    for module_name, funcs in REQUIRED_FUNCTIONS.items():
        module = importlib.import_module(module_name)

        for func in funcs:
            if not hasattr(module, func):
                raise RuntimeError(
                    f"Missing required function: {module_name}.{func}"
                )


def validate_system():
    print("Running startup validation...")

    validate_imports()

    from database import init_db, validate_schema
    init_db()
    validate_schema()

    print("Startup validation OK")
