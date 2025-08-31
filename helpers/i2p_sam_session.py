import logging
import uuid

from event.async_ import (
    AsyncEvent,
)

from helpers.connection import (
    Connection,
)


logger = logging.getLogger(
    __name__,
)


class I2PSAMSession(object):
    __slots__ = (
        '__incoming_data_connection',
        '__incoming_data_connection_status_color',
        '__incoming_data_connection_status_text',
        '__name',
        '__on_incoming_data_connection_status_updated_event',
        '__on_outgoing_data_connection_status_updated_event',
        '__outgoing_data_connection',
        '__outgoing_data_connection_status_color',
        '__outgoing_data_connection_status_text',
    )

    def __init__(
            self,
    ) -> None:
        super().__init__()

        self.__incoming_data_connection: (
            Connection | None
        ) = None

        self.__incoming_data_connection_status_color: str | None = None

        self.__incoming_data_connection_status_text = (
            'Не создано'
        )

        self.__name = self.__generate_name()

        self.__on_incoming_data_connection_status_updated_event = AsyncEvent(
            'OnIncomingDataConnectionStatusUpdatedEvent'
        )

        self.__on_outgoing_data_connection_status_updated_event = AsyncEvent(
            'OnOutgoingDataConnectionStatusUpdatedEvent'
        )

        self.__outgoing_data_connection: (
            Connection | None
        ) = None

        self.__outgoing_data_connection_status_color: str | None = None

        self.__outgoing_data_connection_status_text = (
            'Не создано'
        )

    async def close_incoming_data_connection(
        self,
    ) -> None:
        incoming_data_connection = (
            self.__incoming_data_connection
        )

        if incoming_data_connection is not None:
            incoming_data_connection.close()

            self.__incoming_data_connection = (
                incoming_data_connection  # noqa
            ) = None

    async def close_outgoing_data_connection(
        self,
    ) -> None:
        outgoing_data_connection = (
            self.__outgoing_data_connection
        )

        if outgoing_data_connection is not None:
            outgoing_data_connection.close()

            self.__outgoing_data_connection = (
                outgoing_data_connection  # noqa
            ) = None

    async def fini(
            self,
    ) -> None:
        await self.close_incoming_data_connection()
        await self.close_outgoing_data_connection()

    def get_incoming_data_connection(
            self
    ) -> Connection | None:
        return self.__incoming_data_connection

    def get_incoming_data_connection_status_text(
            self
    ) -> str:
        return self.__incoming_data_connection_status_text

    def get_name(self) -> str:
        return self.__name

    def get_on_incoming_data_connection_status_updated_event(
            self,
    ) -> AsyncEvent:
        return self.__on_incoming_data_connection_status_updated_event

    def get_on_outgoing_data_connection_status_updated_event(
            self,
    ) -> AsyncEvent:
        return self.__on_outgoing_data_connection_status_updated_event

    def get_outgoing_data_connection(
            self
    ) -> Connection | None:
        return self.__outgoing_data_connection

    def get_outgoing_data_connection_status_text(
            self
    ) -> str:
        return self.__outgoing_data_connection_status_text

    def regenerate_name(self) -> None:
        self.__name = self.__generate_name()

    def set_incoming_data_connection(
            self,
            value: Connection | None
    ) -> None:
        self.__incoming_data_connection = value

    def set_outgoing_data_connection(
            self,
            value: Connection | None
    ) -> None:
        self.__outgoing_data_connection = value

    def update_incoming_data_connection_status(
        self,
        new_incoming_data_connection_status_color: str | None,
        new_incoming_data_connection_status_text: str,
    ) -> None:
        old_incoming_data_connection_status_text = self.__incoming_data_connection_status_text

        if (
            old_incoming_data_connection_status_text is not None and (
                new_incoming_data_connection_status_text ==
                old_incoming_data_connection_status_text
            )
        ):
            return

        logger.info(
            'New incoming data connection status text'
            f': {new_incoming_data_connection_status_text!r}'
        )

        self.__incoming_data_connection_status_text = (
            new_incoming_data_connection_status_text
        )

        self.__incoming_data_connection_status_color = (
            new_incoming_data_connection_status_color
        )

        self.__on_incoming_data_connection_status_updated_event(
            color=new_incoming_data_connection_status_color,
            text=new_incoming_data_connection_status_text
        )

    def update_outgoing_data_connection_status(
        self,
        new_outgoing_data_connection_status_color: str | None,
        new_outgoing_data_connection_status_text: str,
    ) -> None:
        old_outgoing_data_connection_status_text = self.__outgoing_data_connection_status_text

        if (
            old_outgoing_data_connection_status_text is not None and (
                new_outgoing_data_connection_status_text ==
                old_outgoing_data_connection_status_text
            )
        ):
            return

        logger.info(
            'New outgoing data connection status text'
            f': {new_outgoing_data_connection_status_text!r}'
        )

        self.__outgoing_data_connection_status_text = (
            new_outgoing_data_connection_status_text
        )

        self.__outgoing_data_connection_status_color = (
            new_outgoing_data_connection_status_color
        )

        self.__on_outgoing_data_connection_status_updated_event(
            color=new_outgoing_data_connection_status_color,
            text=new_outgoing_data_connection_status_text
        )

    @staticmethod
    def __generate_name() -> str:
        return uuid.uuid4().hex