import asyncio
import logging
import traceback
import typing

from concurrent.futures import (
    Future
)

T = typing.TypeVar("T")

logger = logging.getLogger(
    __name__,
)

async def log_exceptions(
        awaitable: typing.Awaitable[T]
) -> T:
    if awaitable is None:
        raise ValueError("awaitable must not be None")

    try:
        return (
            await (
                awaitable
            )
        )
    except Exception as exception:
        logger.error(
            'Unhandled exception: %s',
            "".join(traceback.format_exception(exception))
        )
        raise exception


def create_task_with_exceptions_logging(
        coroutine: typing.Coroutine[typing.Any, typing.Any, T],
        name: str | None = None
) -> asyncio.Task:
    return (
        asyncio.create_task(
            log_exceptions(
                coroutine
            ),

            name=(
                name
            )
        )
    )


def run_coroutine_threadsafe_with_exceptions_logging(
        coroutine: typing.Coroutine[typing.Any, typing.Any, T],
        event_loop: asyncio.AbstractEventLoop
) -> Future:
    return (
        asyncio.run_coroutine_threadsafe(
            log_exceptions(
                coroutine
            ),

            event_loop
        )
    )


def create_task_with_exceptions_logging_threadsafe(
        coroutine: typing.Coroutine[typing.Any, typing.Any, T],
        name: str | None = None
) -> typing.Union[asyncio.Task, Future]:
    try:
        event_loop = (
            asyncio.get_running_loop()
        )
    except RuntimeError:  # Running loop was not found
        event_loop = (
            None
        )

    from globals.common import (
        g_common_globals
    )

    global_event_loop = (
        g_common_globals.get_asyncio_event_loop()
    )

    assert (
        global_event_loop is not None
    ), (
        global_event_loop
    )

    if (
            event_loop is
            global_event_loop
    ):
        return (
            create_task_with_exceptions_logging(
                coroutine,
                name
            )
        )

    return (
        run_coroutine_threadsafe_with_exceptions_logging(
            coroutine,
            global_event_loop
        )
    )
