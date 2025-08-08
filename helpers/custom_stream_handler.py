import logging
import sys


class CustomStreamHandler(logging.StreamHandler):
    __slots__ = (
        '__stderr_stream_handler',
        '__stdout_stream_handler',
    )

    terminator = '\n'

    def __init__(
        self,
    ) -> None:
        super(CustomStreamHandler, self).__init__()

        self.__stderr_stream_handler = logging.StreamHandler(
            stream=sys.stderr,
        )

        self.__stdout_stream_handler = logging.StreamHandler(
            stream=sys.stdout,
        )

    def flush(
        self,
    ) -> None:
        self.acquire()

        try:
            self.__stderr_stream_handler.flush()
            self.__stdout_stream_handler.flush()
        finally:
            self.release()

    def emit(
        self,
        record: logging.LogRecord,
    ):
        level_number = record.levelno

        stream_handler: logging.StreamHandler

        if level_number >= logging.WARNING:
            stream_handler = self.__stderr_stream_handler
        else:
            stream_handler = self.__stdout_stream_handler

        stream_handler.emit(
            record,
        )

    def setStream(
        self,
        stream,
    ):
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'[{self.__class__.__name__}]'
