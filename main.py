import asyncio
import codecs
import logging
import uuid

import sys
import typing

from ipaddress import (
    ip_address,
    IPv4Address,
    IPv6Address
)

import i2plib  # noqa
import orjson

from PyQt6.QtCore import (
    Qt
)

from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLineEdit,
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget
)

from qasync import (
    QEventLoop,
    asyncSlot
)

from utils.json import (
    JsonUtils
)

from utils.qt import (
    QtUtils
)


_CONFIG_FILE_PATH = (
    './'
    'data/'
    'config.json'
)


class _Connection(object):
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
            _Connection,
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


class MainWindow(QMainWindow):
    __slots__ = (
        '__config_raw_data',
        '__conversation_text_edit',
        '__local_i2p_node_address',
        '__local_i2p_node_address_key_label',
        '__local_i2p_node_address_value_label',
        '__local_i2p_node_destination',
        '__local_i2p_node_sam_ip_address',
        '__local_i2p_node_sam_ip_address_line_edit',
        '__local_i2p_node_sam_port',
        '__local_i2p_node_sam_ip_address_raw',
        '__local_i2p_node_sam_port',
        '__local_i2p_node_sam_port_raw',
        '__local_i2p_node_sam_port_line_edit',
        '__local_i2p_node_sam_session_control_connection',
        '__local_i2p_node_sam_session_creation_event',
        '__local_i2p_node_sam_session_status_key_label',
        '__local_i2p_node_sam_session_status_raw',
        '__local_i2p_node_sam_session_status_value_label',
        '__local_i2p_node_sam_session_data_connection',
        '__local_i2p_node_sam_session_data_connection_status_key_label',
        '__local_i2p_node_sam_session_data_connection_status_raw',
        '__local_i2p_node_sam_session_data_connection_status_value_label',
        '__local_i2p_node_sam_session_name',
        '__local_i2p_node_sam_session_update_lock',
        '__remote_i2p_node_address_line_edit',
        '__remote_i2p_node_address_raw',
        '__remote_i2p_node_sam_session_data_connection'
    )

    def __init__(self):
        super(
            MainWindow,
            self
        ).__init__()

        self.setWindowTitle(
            'Secure Messenger'
        )

        config_raw_data: (
            typing.Dict
        ) = (
            JsonUtils.read_if_exists(
                _CONFIG_FILE_PATH,

                default=(
                    dict
                )
            )
        )

        local_i2p_node_destination_raw = (
            config_raw_data.get(
                'local_i2p_node_destination_raw'
            )
        )

        local_i2p_node_destination: (
            typing.Optional[
                i2plib.Destination
            ]
        )

        if local_i2p_node_destination_raw is not None:
            local_i2p_node_destination = (
                i2plib.Destination(
                    data=(
                        local_i2p_node_destination_raw
                    ),

                    has_private_key=(
                        True
                    )
                )
            )
        else:
            local_i2p_node_destination = (
                None
            )

        window_layout_widget = (
            QWidget()
        )

        window_layout = (
            QVBoxLayout(
                window_layout_widget
            )
        )

        # Filling functionality layout

        functionality_layout = (
            QGridLayout()
        )

        local_i2p_node_sam_ip_address_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'IPv4/IPv6-адрес I2P SAM'
                )
            )
        )

        local_i2p_node_sam_ip_address_line_edit = (
            QLineEdit()
        )

        local_i2p_node_sam_ip_address_raw: (
            typing.Optional[
                str
            ]
        ) = (
            config_raw_data.get(
                'local_i2p_node_sam_ip_address_raw'
            )
        )

        if local_i2p_node_sam_ip_address_raw:
            local_i2p_node_sam_ip_address_line_edit.setText(
                local_i2p_node_sam_ip_address_raw
            )

        local_i2p_node_sam_ip_address_line_edit.textChanged.connect(  # noqa
            self.__on_local_i2p_node_sam_ip_address_line_edit_text_changed
        )

        local_i2p_node_sam_port_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'Порт I2P SAM'
                )
            )
        )

        local_i2p_node_sam_port_line_edit = (
            QLineEdit()
        )

        local_i2p_node_sam_port_raw: (
            typing.Optional[
                str
            ]
        ) = (
            config_raw_data.get(
                'local_i2p_node_sam_port_raw'
            )
        )

        if local_i2p_node_sam_port_raw:
            local_i2p_node_sam_port_line_edit.setText(
                local_i2p_node_sam_port_raw
            )

        local_i2p_node_sam_port_line_edit.textChanged.connect(  # noqa
            self.__on_local_i2p_node_sam_port_line_edit_text_changed
        )

        remote_i2p_node_address_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'I2P-адрес удалённого узла'
                )
            )
        )

        remote_i2p_node_address_line_edit = (
            QLineEdit()
        )

        remote_i2p_node_address_raw: (
            typing.Optional[
                str
            ]
        ) = (
            config_raw_data.get(
                'remote_i2p_node_address_raw'
            )
        )

        if remote_i2p_node_address_raw:
            remote_i2p_node_address_line_edit.setText(
                remote_i2p_node_address_raw
            )

        remote_i2p_node_address_line_edit.textChanged.connect(  # noqa
            self.__on_remote_i2p_node_address_line_edit_text_changed
        )

        functionality_layout.addWidget(
            local_i2p_node_sam_ip_address_label,
            0, 0, 1, 1
        )

        functionality_layout.addWidget(
            local_i2p_node_sam_port_label,
            0, 1, 1, 1
        )

        functionality_layout.addWidget(
            local_i2p_node_sam_ip_address_line_edit,
            1, 0, 1, 1
        )

        functionality_layout.addWidget(
            local_i2p_node_sam_port_line_edit,
            1, 1, 1, 1
        )

        functionality_layout.addWidget(
            remote_i2p_node_address_label,
            2, 0, 1, 2
        )

        functionality_layout.addWidget(
            remote_i2p_node_address_line_edit,
            3, 0, 1, 2
        )

        window_layout.addLayout(
            functionality_layout
        )

        # Filling info layout

        info_layout = (
            QGridLayout()
        )

        local_i2p_node_address = (
            self.__get_local_i2p_node_address(
                local_i2p_node_destination
            )
        )

        local_i2p_node_address_key_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'Адрес собственного узла'
                )
            )
        )

        local_i2p_node_address_value_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    local_i2p_node_address
                )
            )
        )

        local_i2p_node_address_value_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        local_i2p_node_sam_session_status_key_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'Статус I2P SAM сессии'
                )
            )
        )

        local_i2p_node_sam_session_status_raw = (
            'Не создана'
        )

        local_i2p_node_sam_session_status_value_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    local_i2p_node_sam_session_status_raw
                )
            )
        )

        local_i2p_node_sam_session_data_connection_status_key_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'Статус входящего I2P SAM подключения'
                )
            )
        )

        local_i2p_node_sam_session_data_connection_status_raw = (
            'Не создано'
        )

        local_i2p_node_sam_session_data_connection_status_value_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    local_i2p_node_sam_session_data_connection_status_raw
                )
            )
        )

        info_layout.addWidget(
            local_i2p_node_address_key_label,
            0, 0, 1, 1
        )

        info_layout.addWidget(
            local_i2p_node_address_value_label,
            0, 1, 1, 1
        )

        info_layout.addWidget(
            local_i2p_node_sam_session_status_key_label,
            1, 0, 1, 1
        )

        info_layout.addWidget(
            local_i2p_node_sam_session_status_value_label,
            1, 1, 1, 1
        )

        info_layout.addWidget(
            local_i2p_node_sam_session_data_connection_status_key_label,
            2, 0, 1, 1
        )

        info_layout.addWidget(
            local_i2p_node_sam_session_data_connection_status_value_label,
            2, 1, 1, 1
        )

        window_layout.addLayout(
            info_layout
        )

        # Filling conversation text edit

        conversation_text_edit = (
            QTextEdit()
        )

        conversation_text_edit.setPlaceholderText(
            'Диалог с собеседником'
        )

        conversation_text_edit.setEnabled(
            False
        )

        window_layout.addWidget(
            conversation_text_edit
        )

        # Set the central widget of the Window.

        self.setCentralWidget(
            window_layout_widget
        )

        # self.setFixedSize(
        #     QSize(
        #         400,
        #         300
        #     )
        # )

        self.setMinimumSize(
            1366,  # 1920
            768    # 1080
        )

        self.setWindowFlags(
            Qt.WindowType(
                Qt.WindowType.WindowMaximizeButtonHint |
                Qt.WindowType.WindowMinimizeButtonHint |
                Qt.WindowType.WindowCloseButtonHint
            )
        )

        self.__config_raw_data = (
            config_raw_data
        )

        self.__conversation_text_edit = (
            conversation_text_edit
        )

        self.__local_i2p_node_address = (
            local_i2p_node_address
        )

        self.__local_i2p_node_address_key_label = (
            local_i2p_node_address_key_label
        )

        self.__local_i2p_node_address_value_label = (
            local_i2p_node_address_value_label
        )

        self.__local_i2p_node_destination = (
            local_i2p_node_destination
        )

        self.__local_i2p_node_sam_ip_address: (
            typing.Optional[
                typing.Union[
                    IPv4Address,
                    IPv6Address
                ]
            ]
        ) = None

        self.__local_i2p_node_sam_ip_address_line_edit = (
            local_i2p_node_sam_ip_address_line_edit
        )

        self.__local_i2p_node_sam_ip_address_raw: (
            typing.Optional[
                str
            ]
        ) = None

        self.__local_i2p_node_sam_port: (
            typing.Optional[
                int
            ]
        ) = None

        self.__local_i2p_node_sam_port_line_edit = (
            local_i2p_node_sam_port_line_edit
        )

        self.__local_i2p_node_sam_port_raw: (
            typing.Optional[
                str
            ]
        ) = None

        self.__local_i2p_node_sam_session_control_connection: (
            typing.Optional[
                _Connection
            ]
        ) = None

        self.__local_i2p_node_sam_session_creation_event = (
            asyncio.Event()
        )

        self.__local_i2p_node_sam_session_status_key_label = (
            local_i2p_node_sam_session_status_key_label
        )

        self.__local_i2p_node_sam_session_status_raw = (
            local_i2p_node_sam_session_status_raw
        )

        self.__local_i2p_node_sam_session_status_value_label = (
            local_i2p_node_sam_session_status_value_label
        )

        self.__local_i2p_node_sam_session_data_connection: (
            typing.Optional[
                _Connection
            ]
        ) = None

        self.__local_i2p_node_sam_session_data_connection_status_key_label = (
            local_i2p_node_sam_session_data_connection_status_key_label
        )

        self.__local_i2p_node_sam_session_data_connection_status_raw = (
            local_i2p_node_sam_session_data_connection_status_raw
        )

        self.__local_i2p_node_sam_session_data_connection_status_value_label = (
            local_i2p_node_sam_session_data_connection_status_value_label
        )

        self.__local_i2p_node_sam_session_name = (
            self.__generate_i2p_node_sam_session_name()
        )

        self.__local_i2p_node_sam_session_update_lock = (
            asyncio.Lock()
        )

        self.__remote_i2p_node_address_line_edit = (
            remote_i2p_node_address_line_edit
        )

        self.__remote_i2p_node_address_raw: (
            typing.Optional[
                str
            ]
        ) = None

        self.__remote_i2p_node_port: (
            typing.Optional[
                int
            ]
        ) = None

        asyncio.create_task(
            self.__on_local_i2p_node_sam_ip_address_line_edit_text_changed_ex()
        )

        asyncio.create_task(
            self.__on_local_i2p_node_sam_port_line_edit_text_changed_ex()
        )

        self.__on_remote_i2p_node_address_line_edit_text_changed()

        self.__update_local_i2p_node_address()

    async def start_connection_listening_loop(
            self
    ) -> None:
        while True:
            if self.__local_i2p_node_sam_session_control_connection is None:
                await (
                    self.__local_i2p_node_sam_session_creation_event.wait()
                )

            local_i2p_node_sam_ip_address = (
                self.__local_i2p_node_sam_ip_address
            )

            if local_i2p_node_sam_ip_address is None:
                await (
                    self.__update_local_i2p_node_sam_session_data_connection_status(
                        'Невозможно создать без адреса собственного узла'
                    )
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

            local_i2p_node_sam_port = (
                self.__local_i2p_node_sam_port
            )

            if local_i2p_node_sam_port is None:
                await (
                    self.__update_local_i2p_node_sam_session_data_connection_status(
                        'Невозможно создать без I2P SAM порта'
                    )
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

            settled_remote_i2p_node_address_raw = (
                self.__remote_i2p_node_address_raw
            )

            if settled_remote_i2p_node_address_raw is None:
                await (
                    self.__update_local_i2p_node_sam_session_data_connection_status(
                        'Невозможно создать без I2P адреса удалённого узла'
                    )
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

            local_i2p_node_sam_ip_address_and_port_pair = (
                str(
                    local_i2p_node_sam_ip_address
                ),

                local_i2p_node_sam_port
            )

            (
                local_i2p_node_sam_session_data_reader,
                local_i2p_node_sam_session_data_writer
            ) = (
                await (
                    i2plib.stream_accept(
                        session_name=(
                            self.__local_i2p_node_sam_session_name
                        ),

                        sam_address=(
                            local_i2p_node_sam_ip_address_and_port_pair
                        )
                    )
                )
            )

            self.__local_i2p_node_sam_session_data_connection = (
                _Connection(
                    local_i2p_node_sam_session_data_reader,
                    local_i2p_node_sam_session_data_writer
                )
            )

            await (
                self.__update_local_i2p_node_sam_session_data_connection_status(
                    'Прослушивание...'
                )
            )

            remote_i2p_node_destination_bytes = (
                await (
                    local_i2p_node_sam_session_data_reader.readline()
                )
            )

            remote_i2p_node_destination_raw = (
                remote_i2p_node_destination_bytes.decode().rstrip()
            )

            remote_i2p_node_destination = (  # TODO: check equality with settled remote I2P node address
                i2plib.Destination(
                    remote_i2p_node_destination_raw
                )
            )

            remote_i2p_node_address_raw = (
                f'{remote_i2p_node_destination.base32}.b32.i2p'
            )

            print(
                'New client'
                f' with remote I2P Node address {remote_i2p_node_address_raw!r}'
                ' was connected!'
            )

            if (
                    remote_i2p_node_address_raw !=
                    settled_remote_i2p_node_address_raw
            ):
                await (
                    self.__update_local_i2p_node_sam_session_data_connection_status(
                        'I2P адрес подключенного клиента не соответствует прописанному'
                    )
                )

                await (
                    self.__close_local_i2p_node_sam_session_data_connection()
                )

                local_i2p_node_sam_session_data_connection = (  # noqa
                    None
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

            await (
                self.__update_local_i2p_node_sam_session_data_connection_status(
                    'Создано'
                )
            )

            # while True:  # TODO

    async def update_local_i2p_node_destination(
            self
    ) -> None:
        if self.__local_i2p_node_destination is not None:
            self.__update_local_i2p_node_address()

            await (
                self.__update_local_i2p_node_sam_session()
            )

            return

        local_i2p_node_sam_ip_address = (
            self.__local_i2p_node_sam_ip_address
        )

        if local_i2p_node_sam_ip_address is None:
            self.__config_raw_data.pop(
                'local_i2p_node_destination_raw',
                None
            )

            self.__update_local_i2p_node_address()

            await (
                self.__update_local_i2p_node_sam_session()
            )

            return

        local_i2p_node_sam_port = (
            self.__local_i2p_node_sam_port
        )

        if local_i2p_node_sam_port is None:
            self.__config_raw_data.pop(
                'local_i2p_node_destination_raw',
                None
            )

            self.__update_local_i2p_node_address()

            await (
                self.__update_local_i2p_node_sam_session()
            )

            return

        local_i2p_node_sam_ip_address_and_port_pair = (
            str(
                local_i2p_node_sam_ip_address
            ),

            local_i2p_node_sam_port
        )

        local_i2p_node_destination = (
            self.__local_i2p_node_destination
        ) = (
            await (
                i2plib.new_destination(
                    sam_address=(
                        local_i2p_node_sam_ip_address_and_port_pair
                    )
                )
            )
        )

        local_i2p_node_destination_raw = (
            local_i2p_node_destination.private_key.base64
        )

        (
            self.__config_raw_data[
                'local_i2p_node_destination_raw'
            ]
        ) = local_i2p_node_destination_raw

        self.__save_config()

        self.__update_local_i2p_node_address()

        await (
            self.__update_local_i2p_node_sam_session()
        )

    async def __close_local_i2p_node_sam_session_control_connection(
            self
    ) -> None:
        local_i2p_node_sam_session_control_connection = (
            self.__local_i2p_node_sam_session_control_connection
        )

        if local_i2p_node_sam_session_control_connection is not None:
            local_i2p_node_sam_session_control_connection.close()

            self.__local_i2p_node_sam_session_control_connection = (
                local_i2p_node_sam_session_control_connection  # noqa
            ) = None

        self.__local_i2p_node_sam_session_creation_event.clear()

    async def __close_local_i2p_node_sam_session_data_connection(
            self
    ) -> None:
        local_i2p_node_sam_session_data_connection = (
            self.__local_i2p_node_sam_session_data_connection
        )

        if local_i2p_node_sam_session_data_connection is not None:
            local_i2p_node_sam_session_data_connection.close()

            self.__local_i2p_node_sam_session_data_connection = (
                local_i2p_node_sam_session_data_connection  # noqa
            ) = None

    @staticmethod
    def __generate_i2p_node_sam_session_name() -> str:
        return (
            uuid.uuid4().hex
        )

    @staticmethod
    def __get_local_i2p_node_address(
            local_i2p_node_destination: (
                typing.Optional[
                    i2plib.Destination
                ]
            )
    ) -> str:
        if local_i2p_node_destination is not None:
            return (
                f'{local_i2p_node_destination.base32}.b32.i2p'
            )

        return (
            'N/A'
        )

    @asyncSlot
    async def __on_local_i2p_node_sam_ip_address_line_edit_text_changed(
            self
    ) -> None:
        await (
            self.__on_local_i2p_node_sam_ip_address_line_edit_text_changed_ex()
        )

    async def __on_local_i2p_node_sam_ip_address_line_edit_text_changed_ex(
            self
    ) -> None:
        local_i2p_node_sam_ip_address_line_edit = (
            self.__local_i2p_node_sam_ip_address_line_edit
        )

        new_local_i2p_node_sam_ip_address_raw = (
            local_i2p_node_sam_ip_address_line_edit.text().strip()
        )

        old_local_i2p_node_sam_ip_address_raw = (
            self.__local_i2p_node_sam_ip_address_raw
        )

        if (
                old_local_i2p_node_sam_ip_address_raw is not None and

                (
                    new_local_i2p_node_sam_ip_address_raw ==
                    old_local_i2p_node_sam_ip_address_raw
                )
        ):
            return

        self.__local_i2p_node_sam_ip_address_raw = (
            new_local_i2p_node_sam_ip_address_raw
        )

        (
            self.__config_raw_data[
                'local_i2p_node_sam_ip_address_raw'
            ]
        ) = new_local_i2p_node_sam_ip_address_raw

        self.__save_config()

        new_local_i2p_node_sam_ip_address: (
            typing.Optional[
                typing.Union[
                    IPv4Address,
                    IPv6Address
                ]
            ]
        )

        try:
            new_local_i2p_node_sam_ip_address = (
                ip_address(
                    new_local_i2p_node_sam_ip_address_raw
                )
            )
        except ValueError:
            print(
                f'Could not parse IP address {new_local_i2p_node_sam_ip_address_raw!r}'
            )

            new_local_i2p_node_sam_ip_address = (
                None
            )

        self.__local_i2p_node_sam_ip_address = (
            new_local_i2p_node_sam_ip_address
        )

        if new_local_i2p_node_sam_ip_address is not None:
            local_i2p_node_sam_ip_address_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(0, 255, 0, 0.25);'
                ' selection-background-color: rgba(0, 255, 0, 0.5);'
                ' }'
            )
        else:
            local_i2p_node_sam_ip_address_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(255, 0, 0, 0.25);'
                ' selection-background-color: rgba(255, 0, 0, 0.5);'
                ' }'
            )

        await (
            self.update_local_i2p_node_destination()
        )

    @asyncSlot
    async def __on_local_i2p_node_sam_port_line_edit_text_changed(
            self
    ) -> None:
        await (
            self.__on_local_i2p_node_sam_port_line_edit_text_changed_ex()
        )

    async def __on_local_i2p_node_sam_port_line_edit_text_changed_ex(
            self
    ) -> None:
        local_i2p_node_sam_port_line_edit = (
            self.__local_i2p_node_sam_port_line_edit
        )

        new_local_i2p_node_sam_port_raw = (
            local_i2p_node_sam_port_line_edit.text().strip()
        )

        old_local_i2p_node_sam_port_raw = (
            self.__local_i2p_node_sam_port_raw
        )

        if (
                old_local_i2p_node_sam_port_raw is not None and

                (
                    new_local_i2p_node_sam_port_raw ==
                    old_local_i2p_node_sam_port_raw
                )
        ):
            return

        self.__local_i2p_node_sam_port_raw = (
            new_local_i2p_node_sam_port_raw
        )

        (
            self.__config_raw_data[
                'local_i2p_node_sam_port_raw'
            ]
        ) = new_local_i2p_node_sam_port_raw

        self.__save_config()

        new_local_i2p_node_sam_port: (
            typing.Optional[
                int
            ]
        )

        if new_local_i2p_node_sam_port_raw.isdigit():
            try:
                new_local_i2p_node_sam_port = (
                    int(
                        new_local_i2p_node_sam_port_raw
                    )
                )

                if not (
                        0 <
                        new_local_i2p_node_sam_port <

                        (
                            1 <<
                            16
                        )
                ):
                    new_local_i2p_node_sam_port = (
                        None
                    )
            except ValueError:
                print(
                    f'Could not parse port {new_local_i2p_node_sam_port_raw!r}'
                )

                new_local_i2p_node_sam_port = (
                    None
                )
        else:
            new_local_i2p_node_sam_port = (
                None
            )

        self.__local_i2p_node_sam_port = (
            new_local_i2p_node_sam_port
        )

        if new_local_i2p_node_sam_port is not None:
            local_i2p_node_sam_port_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(0, 255, 0, 0.25);'
                ' selection-background-color: rgba(0, 255, 0, 0.5);'
                ' }'
            )
        else:
            local_i2p_node_sam_port_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(255, 0, 0, 0.25);'
                ' selection-background-color: rgba(255, 0, 0, 0.5);'
                ' }'
            )

        await (
            self.update_local_i2p_node_destination()
        )

    def __on_remote_i2p_node_address_line_edit_text_changed(
            self
    ) -> None:
        remote_i2p_node_address_line_edit = (
            self.__remote_i2p_node_address_line_edit
        )

        new_remote_i2p_node_address_raw = (
            remote_i2p_node_address_line_edit.text().strip()
        )

        old_remote_i2p_node_address_raw = (
            self.__remote_i2p_node_address_raw
        )

        if (
                old_remote_i2p_node_address_raw is not None and

                (
                    new_remote_i2p_node_address_raw ==
                    old_remote_i2p_node_address_raw
                )
        ):
            return

        self.__remote_i2p_node_address_raw = (
            new_remote_i2p_node_address_raw
        )

        (
            self.__config_raw_data[
                'remote_i2p_node_address_raw'
            ]
        ) = new_remote_i2p_node_address_raw

        self.__save_config()

        if 1:  # TODO: check by regexp match
            remote_i2p_node_address_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(0, 255, 0, 0.25);'
                ' selection-background-color: rgba(0, 255, 0, 0.5);'
                ' }'
            )
        else:
            remote_i2p_node_address_line_edit.setStyleSheet(  # noqa
                'QLineEdit {'
                ' background: rgba(255, 0, 0, 0.25);'
                ' selection-background-color: rgba(255, 0, 0, 0.5);'
                ' }'
            )

    def __save_config(
            self
    ) -> None:
        with (
                codecs.open(
                    _CONFIG_FILE_PATH,
                    'w',
                    'utf-8'
                )
        ) as config_file:
            config_file.write(
                orjson.dumps(
                    self.__config_raw_data
                ).decode()
            )

    def __update_local_i2p_node_address(
            self
    ) -> None:
        new_local_i2p_node_address = (
            self.__get_local_i2p_node_address(
                self.__local_i2p_node_destination
            )
        )

        old_local_i2p_node_address = (
            self.__local_i2p_node_address
        )

        if (
                old_local_i2p_node_address is not None and

                (
                    new_local_i2p_node_address ==
                    old_local_i2p_node_address
                )
        ):
            return

        self.__local_i2p_node_address = (
            new_local_i2p_node_address
        )

        self.__local_i2p_node_address_value_label.setText(
            new_local_i2p_node_address
        )

    async def __update_local_i2p_node_sam_session(
            self
    ):
        async with self.__local_i2p_node_sam_session_update_lock:
            if self.__local_i2p_node_sam_session_control_connection is not None:
                return

            local_i2p_node_destination = (
                self.__local_i2p_node_destination
            )

            if local_i2p_node_destination is None:
                await (
                    self.__close_local_i2p_node_sam_session_data_connection()
                )

                await (
                    self.__close_local_i2p_node_sam_session_control_connection()
                )

                await (
                    self.__update_local_i2p_node_sam_session_status(
                        'Невозможно создать без адреса собственного узла'
                    )
                )

                return

            local_i2p_node_sam_ip_address = (
                self.__local_i2p_node_sam_ip_address
            )

            if local_i2p_node_sam_ip_address is None:
                await (
                    self.__close_local_i2p_node_sam_session_data_connection()
                )

                await (
                    self.__close_local_i2p_node_sam_session_control_connection()
                )

                await (
                    self.__update_local_i2p_node_sam_session_status(
                        'Невозможно создать без I2P SAM адреса'
                    )
                )

                return

            local_i2p_node_sam_port = (
                self.__local_i2p_node_sam_port
            )

            if local_i2p_node_sam_port is None:
                await (
                    self.__close_local_i2p_node_sam_session_data_connection()
                )

                await (
                    self.__close_local_i2p_node_sam_session_control_connection()
                )

                await (
                    self.__update_local_i2p_node_sam_session_status(
                        'Невозможно создать без I2P SAM порта'
                    )
                )

                return

            await (
                self.__update_local_i2p_node_sam_session_status(
                    'Попытка создания...'
                )
            )

            local_i2p_node_sam_ip_address_and_port_pair = (
                str(
                    local_i2p_node_sam_ip_address
                ),

                local_i2p_node_sam_port
            )

            while True:
                try:
                    (
                        local_i2p_node_sam_session_control_reader,
                        local_i2p_node_sam_session_control_writer
                    ) = (
                        await (
                            asyncio.wait_for(
                                i2plib.create_session(
                                    session_name=(
                                        self.__local_i2p_node_sam_session_name
                                    ),

                                    sam_address=(
                                        local_i2p_node_sam_ip_address_and_port_pair
                                    ),

                                    destination=(
                                        local_i2p_node_destination
                                    )
                                ),

                                timeout=(
                                    60.0 *  # s
                                    1.0     # m
                                )
                            )
                        )
                    )

                    break
                except TimeoutError:
                    self.__local_i2p_node_sam_session_name = (
                        self.__generate_i2p_node_sam_session_name()
                    )

                    continue

            self.__local_i2p_node_sam_session_control_connection = (
                _Connection(
                    local_i2p_node_sam_session_control_reader,
                    local_i2p_node_sam_session_control_writer
                )
            )

            await (
                self.__update_local_i2p_node_sam_session_status(
                    'Создана'
                )
            )

            self.__local_i2p_node_sam_session_creation_event.set()

    async def __update_local_i2p_node_sam_session_data_connection_status(
            self,

            new_local_i2p_node_sam_session_data_connection_status_raw: str
    ) -> None:
        local_i2p_node_sam_session_data_connection_status_value_label = (
            self.__local_i2p_node_sam_session_data_connection_status_value_label
        )

        old_local_i2p_node_sam_session_data_connection_status_raw = (
            local_i2p_node_sam_session_data_connection_status_value_label.text().strip()
        )

        if (
                old_local_i2p_node_sam_session_data_connection_status_raw is not None and

                (
                    new_local_i2p_node_sam_session_data_connection_status_raw ==
                    old_local_i2p_node_sam_session_data_connection_status_raw
                )
        ):
            return

        local_i2p_node_sam_session_data_connection_status_value_label.setText(
            new_local_i2p_node_sam_session_data_connection_status_raw
        )

        print(
            new_local_i2p_node_sam_session_data_connection_status_raw
        )

        self.__local_i2p_node_sam_session_data_connection_status_raw = (
            new_local_i2p_node_sam_session_data_connection_status_raw
        )

    async def __update_local_i2p_node_sam_session_status(
            self,

            new_local_i2p_node_sam_session_status_raw: str
    ) -> None:
        local_i2p_node_sam_session_status_value_label = (
            self.__local_i2p_node_sam_session_status_value_label
        )

        old_local_i2p_node_sam_session_status_raw = (
            local_i2p_node_sam_session_status_value_label.text().strip()
        )

        if (
                old_local_i2p_node_sam_session_status_raw is not None and

                (
                    new_local_i2p_node_sam_session_status_raw ==
                    old_local_i2p_node_sam_session_status_raw
                )
        ):
            return

        local_i2p_node_sam_session_status_value_label.setText(
            new_local_i2p_node_sam_session_status_raw
        )

        print(
            new_local_i2p_node_sam_session_status_raw
        )

        self.__local_i2p_node_sam_session_status_raw = (
            new_local_i2p_node_sam_session_status_raw
        )


async def run_application(
        application: (
            QApplication
        )
) -> None:
    application_close_event = (
        asyncio.Event()
    )

    application.aboutToQuit.connect(  # noqa
        application_close_event.set
    )

    window = (
        MainWindow()
    )

    window.show()

    # Step 1: create destination if needed

    asyncio.create_task(
        window.update_local_i2p_node_destination()
    )

    # application.exec()

    # with py_qt_event_loop:
    #     py_qt_event_loop.run_forever()

    await (
        asyncio.gather(
            window.start_connection_listening_loop(),
            application_close_event.wait()
        )
    )


def main() -> None:
    logging.basicConfig(
        level=(
            logging.DEBUG
        )
    )

    # create PyQt6 application

    application = (
        QApplication(
            sys.argv
        )
    )

    py_qt_event_loop = (
        QEventLoop(
            application
        )
    )

    # py_qt_event_loop.set_debug(
    #     True
    # )

    asyncio.set_event_loop(
        py_qt_event_loop
    )

    py_qt_event_loop.run_until_complete(
        run_application(
            application
        )
    )
    # asyncio.run(
    #     run_application(
    #         application
    #     )
    # )


if (
        __name__ ==
        '__main__'
):
    main()
