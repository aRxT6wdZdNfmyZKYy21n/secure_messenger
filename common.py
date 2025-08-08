import typing


class Constants(object):
    # A coroutine function with any args returning any awaitable result
    AsyncFunctionType = typing.Callable[
        ...,  # arbitrary positional/keyword parameters
        typing.Awaitable[typing.Any],
    ]

    class Path(object):
        DataDirectory = './data/'
