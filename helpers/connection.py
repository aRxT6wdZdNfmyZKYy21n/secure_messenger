import asyncio
import logging
import typing

import orjson


logger = (
    logging.getLogger(
        __name__
    )
)


class Connection(object):
    __slots__ = (
        '__reader',
        '__writer'
    )

    def __init__(
            self,

            reader: (
                asyncio.StreamReader
            ),

            writer: (
                asyncio.StreamWriter
            ),
    ) -> None:
        super(
            Connection,
            self
        ).__init__()

        self.__reader = (
            reader
        )

        self.__writer = (
            writer
        )

    def close(
            self
    ) -> None:
        self.__writer.close()

    async def read_raw_data(
            self
    ) -> (
            typing.Optional[
                typing.Dict
            ]
    ):
        line_bytes = (
            await (
                self.__reader.readline()
            )
        )

        if not line_bytes:
            return None

        line = (
            line_bytes.rstrip().decode()
        )

        raw_data = (
            orjson.loads(
                line
            )
        )

        logger.info(
            'Received raw_data'
            f': {raw_data}'
        )

        return (
            raw_data
        )

    def send_raw_data(
            self,

            raw_data: (
                typing.Dict
            )
    ) -> bool:
        self.__writer.write(
            orjson.dumps(
                raw_data
            ) +

            b'\n'
        )

        logger.info(
            'Sent raw data'
            f': {raw_data}'
        )

        return True
