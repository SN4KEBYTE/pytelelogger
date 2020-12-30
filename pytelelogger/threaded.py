from threading import Thread


def threaded(fun):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fun, args=args, kwargs=kwargs)
        thread.start()

        return thread

    return wrapper
