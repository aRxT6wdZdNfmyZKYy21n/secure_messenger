import logging
import uuid

from ipaddress import (
    IPv4Address,
    IPv6Address
)

import i2plib  # noqa

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

    async def create_incoming_data_connection(
            self,

            ip_address: IPv4Address | IPv6Address | None,
            port: int | None,
    ) -> bool:
        if ip_address is None:
            self.update_incoming_data_connection_status(
                new_incoming_data_connection_status_color='red',
                new_incoming_data_connection_status_text='Невозможно создать без адреса собственного узла',
            )

            return False

        if port is None:
            self.update_incoming_data_connection_status(
                new_incoming_data_connection_status_color='red',
                new_incoming_data_connection_status_text='Невозможно создать без I2P SAM порта',
            )

            return False

        ip_address_and_port_pair = (
            str(ip_address),
            port,
        )

        try:
            (
                incoming_data_reader,
                incoming_data_writer,
            ) = await i2plib.stream_accept(
                session_name=self.__name,
                sam_address=ip_address_and_port_pair,
            )
        except i2plib.exceptions.InvalidId:
            self.update_incoming_data_connection_status(
                new_incoming_data_connection_status_color='red',
                new_incoming_data_connection_status_text='Ошибка: сессии не существует',
            )

            # TODO: event

            # await self.__close_local_i2p_node_sam_session_control_connection()

            await self.close_incoming_data_connection()

            # await self.__update_local_i2p_node_sam_session()

            return False

        self.__incoming_data_connection = Connection(
            incoming_data_reader,
            incoming_data_writer,
        )

        self.update_incoming_data_connection_status(
            new_incoming_data_connection_status_color=None,
            new_incoming_data_connection_status_text='Прослушивание...',
        )

        return True

    async def create_outgoing_data_connection(
            self,

            ip_address: IPv4Address | IPv6Address | None,
            port: int | None,
            remote_node_address_raw: str | None,
    ) -> bool:
        if ip_address is None:
            self.update_outgoing_data_connection_status(
                new_outgoing_data_connection_status_color='red',
                new_outgoing_data_connection_status_text='Невозможно создать без адреса собственного узла',
            )

            return False

        if port is None:
            self.update_outgoing_data_connection_status(
                new_outgoing_data_connection_status_color='red',
                new_outgoing_data_connection_status_text='Невозможно создать без I2P SAM порта',
            )

            return False

        if remote_node_address_raw is None:
            self.update_outgoing_data_connection_status(
                new_outgoing_data_connection_status_color='red',
                new_outgoing_data_connection_status_text='Невозможно создать без I2P адреса удалённого узла',
            )

            return False

        is_remote_node_address_raw_valid = self.__is_node_address_raw_valid(
            remote_node_address_raw,
        )

        if not is_remote_node_address_raw_valid:
            self.update_outgoing_data_connection_status(
                new_outgoing_data_connection_status_color='red',
                new_outgoing_data_connection_status_text='I2P адрес удалённого узла некорректен',
            )

            return False

        self.update_outgoing_data_connection_status(
            new_outgoing_data_connection_status_color=None,
            new_outgoing_data_connection_status_text='Попытка создания...',
        )

        local_i2p_node_sam_ip_address_and_port_pair = (
            str(ip_address),
            port,
        )

        try:
            (
                outgoing_data_reader,
                outgoing_data_writer,
            ) = await i2plib.stream_connect(
                destination=remote_node_address_raw,
                session_name=self.__name,
                sam_address=local_i2p_node_sam_ip_address_and_port_pair,
            )
        except i2plib.exceptions.CantReachPeer:
            self.update_outgoing_data_connection_status(
                new_outgoing_data_connection_status_color='red',
                new_outgoing_data_connection_status_text='Не удалось подключиться к удалённому узлу',
            )

            return False
        except i2plib.exceptions.InvalidId:
            self.update_outgoing_data_connection_status(
                new_outgoing_data_connection_status_color='red',
                new_outgoing_data_connection_status_text='Ошибка: сессии не существует',
            )

            # TODO: event

            # await self.__close_local_i2p_node_sam_session_control_connection()

            # await self.__update_local_i2p_node_sam_session()

            return False
        except i2plib.exceptions.InvalidKey:
            self.update_outgoing_data_connection_status(
                new_outgoing_data_connection_status_color='red',
                new_outgoing_data_connection_status_text='Ошибка: некорректный I2P адрес удалённого узла',
            )

            return False

        self.__outgoing_data_connection = Connection(
            outgoing_data_reader,
            outgoing_data_writer,
        )

        self.update_outgoing_data_connection_status(
            new_outgoing_data_connection_status_color='green',
            new_outgoing_data_connection_status_text='Создано',
        )

        logger.info(
            'Successfully connected to client'
            f' with remote I2P Node address {remote_node_address_raw!r}'
        )

        return True

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

    @staticmethod
    def __is_node_address_raw_valid(
        node_address_raw: str,
    ) -> bool:
        return node_address_raw.endswith(
            '.i2p',
        )
