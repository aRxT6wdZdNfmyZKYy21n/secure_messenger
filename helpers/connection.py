import asyncio
import logging
import struct
import typing

import orjson


logger = logging.getLogger(
    __name__,
)


_DEFAULT_TIMEOUT = 15.0  # s


class Connection(object):
    __slots__ = (
        '__reader',
        '__writer',
    )

    def __init__(
        self,
        reader: (asyncio.StreamReader),
        writer: (asyncio.StreamWriter),
    ) -> None:
        super(Connection, self).__init__()

        self.__reader = reader

        self.__writer = writer

    def close(
        self,
    ) -> None:
        self.__writer.close()

    async def read_raw_data(
        self,
        timeout=(_DEFAULT_TIMEOUT),
    ) -> dict | None:
        line_bytes_count_bytes = await self.__read_exactly(
            bytes_count=(4),
            timeout=(timeout),
        )

        if line_bytes_count_bytes is None:
            return None

        line_bytes_count = struct.unpack(
            '!I',
            line_bytes_count_bytes,
        )[0]

        logger.info(
            f'Reading {line_bytes_count} bytes...',
        )

        line_bytes = await self.__read_exactly(
            bytes_count=(line_bytes_count),
            timeout=(timeout),
        )

        if line_bytes is None:
            return None

        line = line_bytes.rstrip().decode()

        raw_data = orjson.loads(
            line,
        )

        logging_raw_data = self.__get_trimmed_data(
            raw_data,
        )

        logger.info(
            f'Received raw_data: {logging_raw_data}',
        )

        return raw_data

    def send_raw_data(
        self,
        raw_data: (dict),
    ) -> bool:
        raw_data_bytes = orjson.dumps(
            raw_data,
        )

        raw_data_bytes_count = len(
            raw_data_bytes,
        )

        raw_data_bytes_count_bytes = struct.pack(
            '!I',
            raw_data_bytes_count,
        )

        writer = self.__writer

        writer.write(
            raw_data_bytes_count_bytes,
        )

        writer.write(
            raw_data_bytes,
        )

        logging_raw_data = self.__get_trimmed_data(
            raw_data,
        )

        logger.info(
            f'Sent raw data: {logging_raw_data}',
        )

        return True

    @classmethod
    def __get_trimmed_data(
        cls,
        data: (typing.Any),
    ) -> typing.Any:
        data_type = type(
            data,
        )

        if data_type is str:
            if len(data) > 64:
                data = data[:64] + '...'
        elif data_type is list:
            return list(
                map(
                    cls.__get_trimmed_data,
                    data,
                ),
            )
        elif data_type is dict:
            return {
                key: (
                    cls.__get_trimmed_data(
                        value,
                    )
                )
                for key, value in (data.items())
            }

        return data

    async def __read_exactly(
        self,
        bytes_count: int,
        timeout=(_DEFAULT_TIMEOUT),
    ) -> bytes | None:
        reader = self.__reader

        try:
            data_bytes = await asyncio.wait_for(
                reader.readexactly(bytes_count),
                timeout=(timeout),
            )
        except asyncio.exceptions.IncompleteReadError:
            logger.warning(
                'IncompleteReadError',
            )

            return None
        except asyncio.TimeoutError:
            logger.warning(
                'Timeout',
            )

            return None

        assert len(data_bytes) == bytes_count, data_bytes

        return data_bytes
