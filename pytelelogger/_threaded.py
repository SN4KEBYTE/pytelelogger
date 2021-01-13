from threading import Thread


def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer


@parametrized
def threaded(fun, daemon=False):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fun, daemon=daemon, args=args, kwargs=kwargs)
        thread.start()

        return thread

    return wrapper
