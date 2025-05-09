import typing


class Constants(object):
    AsyncFunctionType = (
        typing.Callable[
            [
                typing.Any,
                typing.Any
            ],
            typing.Awaitable[
                typing.Any
            ]
        ]
    )

    class Path(object):
        DataDirectory = (
            './'
            'data/'
        )
