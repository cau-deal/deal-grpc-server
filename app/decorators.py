def verified(func):
    # args[0] => self, args[1] => request, args[2] => context
    def wrapper(*args, **kw):
        return func(*args, **kw) if args[2].verified else None

    return wrapper


def unverified(func):
    # args[0] => self, args[1] => request, args[2] => context
    def wrapper(*args, **kw):
        return func(*args, **kw)

    return wrapper
