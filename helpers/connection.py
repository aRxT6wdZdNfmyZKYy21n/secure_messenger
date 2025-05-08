import asyncio
import logging
import struct
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
        reader = (
            self.__reader
        )

        line_bytes_count_bytes = (
            await (
                reader.readexactly(
                    4
                )
            )
        )

        assert (
            len(
                line_bytes_count_bytes
            ) ==

            4
        ), (
            line_bytes_count_bytes
        )

        line_bytes_count = (
            struct.unpack(
                '!I',
                line_bytes_count_bytes
            )[
                0
            ]
        )

        print(
            f'Reading {line_bytes_count} bytes...'
        )

        line_bytes = (
            await (
                self.__reader.readexactly(
                    line_bytes_count
                )
            )
        )

        assert (
            len(
                line_bytes
            ) ==

            line_bytes_count
        ), (
            line_bytes
        )

        line = (
            line_bytes.rstrip().decode()
        )

        raw_data = (
            orjson.loads(
                line
            )
        )

        logging_raw_data = (
            self.__get_trimmed_data(
                raw_data
            )
        )

        logger.info(
            'Received raw_data'
            f': {logging_raw_data}'
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
        raw_data_bytes = (
            orjson.dumps(
                raw_data
            )
        )

        raw_data_bytes_count = (
            len(
                raw_data_bytes
            )
        )

        raw_data_bytes_count_bytes = (
            struct.pack(
                '!I',
                raw_data_bytes_count
            )
        )

        writer = (
            self.__writer
        )

        writer.write(
            raw_data_bytes_count_bytes
        )

        writer.write(
            raw_data_bytes
        )

        logging_raw_data = (
            self.__get_trimmed_data(
                raw_data
            )
        )

        logger.info(
            'Sent raw data'
            f': {logging_raw_data}'
        )

        return True

    @classmethod
    def __get_trimmed_data(
            cls,

            data: (
                typing.Any
            )
    ) -> (
            typing.Any
    ):
        data_type = (
            type(
                data
            )
        )

        if (
                data_type is
                str
        ):
            if (
                    len(
                        data
                    ) >

                    64
            ):
                data = (
                    data[
                        :64
                    ] +

                    '...'
                )
        elif (
                data_type is
                list
        ):
            return (
                list(
                    map(
                        cls.__get_trimmed_data,
                        data
                    )
                )
            )
        elif (
                data_type is
                dict
        ):
            return {
                key: (
                    cls.__get_trimmed_data(
                        value
                    )
                )

                for key, value in (
                    data.items()
                )
            }

        return (
            data
        )
