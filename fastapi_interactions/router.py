from .models import (
    Command,
    CommandMeta,
    Option
)

class CommandRouter:
    def __init__(self):
        self.commands: dict[str, Command] = {}

    def command(self, name: str, description: str):
        def decorator(func):
            meta = getattr(func, '__command_meta__', CommandMeta(name='', description='', type=1))
            meta.name = name
            meta.description = description
            self.commands[name] = Command(callback=func, meta=meta)
            func.__dict__.pop('__command_meta__', None)
            return func
        return decorator
    
def option(name: str, description: str, type: int = 3, required: bool = True):
    def decorator(func):
        meta = getattr(func, "__command__meta__", CommandMeta(name='', description='', type=1))
        meta.options.insert(0, Option(name=name, description=description, type=type))
        func.__command_meta__ = meta
        return func
    return decorator