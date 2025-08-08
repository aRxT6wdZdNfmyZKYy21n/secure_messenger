import os
import typing

import orjson


T = typing.TypeVar("T")


class JsonUtils(object):
    @staticmethod
    def read(
            path: str,
    ) -> typing.Any:
        with open(
            path,
            'r',
            encoding='utf-8'
        ) as json_file:
            return orjson.loads(json_file.read())

    @classmethod
    def read_if_exists(
            cls,
            path: str,
            default: typing.Callable[[], T],
    ) -> typing.Union[typing.Any, T]:
        if not (
                os.path.exists(
                    path,
                )
        ):
            return default()

        return cls.read(path,)
