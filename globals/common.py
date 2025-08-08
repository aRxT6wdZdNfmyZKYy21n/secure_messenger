import asyncio
import typing


__all__ = (
    'g_common_globals',
)


class CommonGlobals(object):
    __slots__ = (
        '__asyncio_event_loop',
    )

    def __init__(
            self
    ) -> None:
        super(
            CommonGlobals,
            self
        ).__init__()

        self.__asyncio_event_loop: (
            asyncio.AbstractEventLoop | None
        ) = None

    def get_asyncio_event_loop(
            self
    ) -> (
            asyncio.AbstractEventLoop | None
    ):
        return (
            self.__asyncio_event_loop
        )

    def init_asyncio_event_loop(
            self,

            value: (
                asyncio.AbstractEventLoop
            )
    ) -> None:
        asyncio_event_loop = (
            self.__asyncio_event_loop
        )

        assert (
            asyncio_event_loop is None
        ), (
            asyncio_event_loop
        )

        self.__asyncio_event_loop = (
            value
        )


g_common_globals = (
    CommonGlobals()
)
