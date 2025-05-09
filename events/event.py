import traceback
import typing
import inspect

from common import (
    Constants
)


class Event(object):
    __slots__ = (
        '__name',
        '__sync_delegates'
    )

    def __init__(
            self,

            name: str
    ) -> None:
        super(
            Event,
            self
        ).__init__()

        self.__name = (
            name
        )

        self.__sync_delegates: (
            typing.List[
                typing.Callable
            ]
        ) = []

    def __iadd__(
            self,

            delegate: (
                typing.Union[
                    typing.Callable,
                    Constants.AsyncFunctionType
                ]
            )
    ) -> (
            typing.Self
    ):
        delegates = (
            self._get_container(
                delegate
            )
        )

        if (
                delegate not in
                delegates
        ):
            delegates.append(
                delegate
            )

        return self

    def __isub__(
            self,

            delegate: (
                typing.Union[
                    typing.Callable,
                    Constants.AsyncFunctionType
                ]
            )
    ) -> (
            typing.Self
    ):
        delegates = (
            self._get_container(
                delegate
            )
        )

        if (
                delegate in
                delegates
        ):
            delegates.remove(
                delegate
            )

        return self

    def __call__(
            self,

            *args,
            **kwargs
    ) -> None:
        name = (
            self.__name
        )

        for delegate in (
                self.__sync_delegates
        ):
            try:
                delegate(
                    *args,
                    **kwargs
                )
            except Exception as exception:
                print(
                    'Handled exception while calling event'
                    f' with name {name!r}'
                    f': {"".join(traceback.format_exception(exception))}'
                )

    def clear(
            self
    ) -> None:
        self.__sync_delegates.clear()

    def get_name(
            self
    ) -> str:
        return (
            self.__name
        )

    def _get_container(
            self,

            delegate: (
                typing.Union[
                    typing.Callable,
                    Constants.AsyncFunctionType
                ]
            )
    ):
        if (
                inspect.iscoroutinefunction(
                    delegate
                )
        ):
            raise (
                NotImplementedError
            )

        return (
            self.__sync_delegates
        )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            '{'
            f'name: {self.__name}'
            '}'
        )
