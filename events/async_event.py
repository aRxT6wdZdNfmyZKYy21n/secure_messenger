import asyncio
import inspect
import typing

from common import (
    Constants
)

from events.event import (
    Event
)

from utils.async_ import (
    create_task_with_exceptions_logging_threadsafe
)


# Async version of Event class
class AsyncEvent(Event):
    __slots__ = (
        '__async_delegates',
    )

    def __init__(
            self,

            name: str
    ) -> None:
        super(
            AsyncEvent,
            self
        ).__init__(
            name
        )

        self.__async_delegates: (
            list[
                Constants.AsyncFunctionType
            ]
        ) = []

    def __call__(
            self,

            *args,
            **kwargs
    ) -> None:
        super(
            AsyncEvent,
            self
        ).__call__(
            *args,
            **kwargs
        )

        create_task_with_exceptions_logging_threadsafe(
            self.__call_event_via_gather(
                *args,
                **kwargs
            )
        )

        """ 3rd way - call event handlers when execution handle will be freed """
        """
        for delegate in (
                self.__async_delegates
        ):
            create_task_with_exceptions_logging_threadsafe(
                delegate(
                    *args,
                    **kwargs
                ),

                name
            )
        """

    def clear(
            self
    ) -> None:
        super(
            AsyncEvent,
            self
        ).clear()

        self.__async_delegates.clear()

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
            return (
                self.__async_delegates
            )

        return (
            super(
                AsyncEvent,
                self
            )._get_container(
                delegate
            )
        )

    """ 1st way - via traditional gather """

    async def __call_event_via_gather(
            self,

            *args,
            **kwargs
    ) -> None:
        await (
            asyncio.gather(
                *(
                    delegate(
                        *args,
                        **kwargs
                    )

                    for delegate in (
                        self.__async_delegates
                    )
                )
            )
        )

    """ 2nd way - from Python 3.11 """
    """
    async def __call_event_via_task_group(
            self,

            *args,
            **kwargs
    ) -> None:
        async with (
            asyncio.TaskGroup()
        ) as task_group:
            for delegate in (
                    self._delegates
            ):
                task_group.create_task(
                    delegate(
                        *args,
                        **kwargs
                    )
                )
    """
