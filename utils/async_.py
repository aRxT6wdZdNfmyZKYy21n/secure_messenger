import asyncio
import traceback
import typing

from concurrent.futures import (
    Future
)


async def log_exceptions(
        awaitable: (
            typing.Awaitable
        )
) -> (
        typing.Any  # TODO: is type correct?
):
    assert (  # TODO: remove
        awaitable is not None
    ), (
        awaitable
    )

    try:
        return (
            await (
                awaitable
            )
        )
    except Exception as exception:
        print(
            'Unhandled exception'
            f': {"".join(traceback.format_exception(exception))}'
        )

        raise (
            exception
        )


def create_task_with_exceptions_logging(
        coroutine: typing.Coroutine,

        name: (
            typing.Optional[
                str
            ]
        ) = None
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
        coroutine: (
            typing.Coroutine
        ),

        event_loop: (
            asyncio.AbstractEventLoop
        )
) -> (
        Future
):
    return (
        asyncio.run_coroutine_threadsafe(
            log_exceptions(
                coroutine
            ),

            event_loop
        )
    )


def create_task_with_exceptions_logging_threadsafe(
        coroutine: (
            typing.Coroutine
        ),

        name: (
            typing.Optional[
                str
            ]
        ) = None
) -> (
        typing.Union[
            asyncio.Task,
            Future
        ]
):
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
