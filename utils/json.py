import codecs
import os
import typing

import orjson


class JsonUtils(object):
    @staticmethod
    def read(
            path: str
    ) -> None:
        with (
                codecs.open(
                    path,
                    'r',
                    'utf-8'
                )
        ) as json_file:
            return (
                orjson.loads(
                    json_file.read()
                )
            )

    @classmethod
    def read_if_exists(
            cls,

            path: str,

            default: (
                typing.Type
            )
    ):
        if not (
                os.path.exists(
                    path
                )
        ):
            return (
                default()
            )

        return (
            cls.read(
                path
            )
        )
