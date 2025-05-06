import asyncio
import codecs
import io
import logging
import os
import uuid

import sys
import typing

from collections import (
    defaultdict
)

from datetime import (
    datetime,
    timezone
)

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
    QPushButton,
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

from utils.time import (
    get_aware_current_timestamp_ms
)


_CONFIG_FILE_NAME = (
    os.getenv(
        'CONFIG_FILE_NAME',
        'config.json'
    )
)

_CONFIG_FILE_PATH = (
    './'
    'data/' +
    _CONFIG_FILE_NAME
)

_IS_DEBUG_RAW = (
    os.getenv(
        'IS_DEBUG',
        'false'
    )
)

_IS_DEBUG: bool

if (
        _IS_DEBUG_RAW ==
        'true'
):
    _IS_DEBUG = (
        True
    )
elif (
        _IS_DEBUG_RAW ==
        'false'
):
    _IS_DEBUG = (
        False
    )
else:
    raise (
        ValueError(
            _IS_DEBUG_RAW
        )
    )


logger = (
    logging.getLogger(
        __name__
    )
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


class _CustomStreamHandler(logging.StreamHandler):
    __slots__ = (
        '__stderr_stream_handler',
        '__stdout_stream_handler'
    )

    terminator = '\n'

    def __init__(
            self
    ):
        super(
            _CustomStreamHandler,
            self
        ).__init__()

        self.__stderr_stream_handler = (
            logging.StreamHandler(
                stream=(
                    sys.stderr
                )
            )
        )

        self.__stdout_stream_handler = (
            logging.StreamHandler(
                stream=(
                    sys.stdout
                )
            )
        )

    def flush(
            self
    ) -> None:
        self.acquire()

        try:
            self.__stderr_stream_handler.flush()
            self.__stdout_stream_handler.flush()
        finally:
            self.release()

    def emit(
            self,

            record: (
                logging.LogRecord
            )
    ):
        level_number = (
            record.levelno
        )

        stream_handler: (
            logging.StreamHandler
        )

        if (
                level_number >=
                logging.WARNING
        ):
            stream_handler = (
                self.__stderr_stream_handler
            )
        else:
            stream_handler = (
                self.__stdout_stream_handler
            )

        stream_handler.emit(
            record
        )

    def setStream(
            self,

            stream
    ):
        raise (
            NotImplementedError
        )

    def __repr__(
            self
    ) -> str:
        return (
            f'[{self.__class__.__name__}]'
        )


class MainWindow(QMainWindow):
    __slots__ = (
        '__config_raw_data',
        '__conversation_text_edit',
        '__last_remote_i2p_node_ping_timestamp_ms',
        '__local_i2p_node_address',
        '__local_i2p_node_address_key_label',
        '__local_i2p_node_address_value_label',
        '__local_i2p_node_destination',
        '__local_i2p_node_message_raw_data_by_id_map',
        '__local_i2p_node_pending_message_raw_data_by_id_map',
        '__local_i2p_node_sam_ip_address',
        '__local_i2p_node_sam_ip_address_line_edit',
        '__local_i2p_node_sam_port',
        '__local_i2p_node_sam_ip_address_raw',
        '__local_i2p_node_sam_port',
        '__local_i2p_node_sam_port_raw',
        '__local_i2p_node_sam_port_line_edit',
        '__local_i2p_node_sam_session_control_connection',
        '__local_i2p_node_sam_session_creation_event',
        '__local_i2p_node_sam_session_incoming_data_connection',
        '__local_i2p_node_sam_session_incoming_data_connection_status_key_label',
        '__local_i2p_node_sam_session_incoming_data_connection_status_raw',
        '__local_i2p_node_sam_session_incoming_data_connection_status_value_label',
        '__local_i2p_node_sam_session_name',
        '__local_i2p_node_sam_session_outgoing_data_connection',
        '__local_i2p_node_sam_session_outgoing_data_connection_status_key_label',
        '__local_i2p_node_sam_session_outgoing_data_connection_status_raw',
        '__local_i2p_node_sam_session_outgoing_data_connection_status_value_label',
        '__local_i2p_node_sam_session_status_key_label',
        '__local_i2p_node_sam_session_status_raw',
        '__local_i2p_node_sam_session_status_value_label',
        '__local_i2p_node_sam_session_update_lock',
        '__message_send_button',
        '__message_text_edit',
        '__remote_i2p_node_address_line_edit',
        '__remote_i2p_node_address_raw',
        '__remote_i2p_node_message_raw_data_by_id_map',
        '__remote_i2p_node_status_key_label',
        '__remote_i2p_node_status_raw',
        '__remote_i2p_node_status_value_label'
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
                'local_i2p_node_sam_ip_address_raw',
                '127.0.0.1'
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
                'local_i2p_node_sam_port_raw',
                '7656'
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

        local_i2p_node_sam_session_incoming_data_connection_status_key_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'Статус входящего I2P SAM подключения'
                )
            )
        )

        local_i2p_node_sam_session_incoming_data_connection_status_raw = (
            'Не создано'
        )

        local_i2p_node_sam_session_incoming_data_connection_status_value_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    local_i2p_node_sam_session_incoming_data_connection_status_raw
                )
            )
        )

        local_i2p_node_sam_session_outgoing_data_connection_status_key_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'Статус исходящего I2P SAM подключения'
                )
            )
        )

        local_i2p_node_sam_session_outgoing_data_connection_status_raw = (
            'Не создано'
        )

        local_i2p_node_sam_session_outgoing_data_connection_status_value_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    local_i2p_node_sam_session_outgoing_data_connection_status_raw
                )
            )
        )

        remote_i2p_node_status_key_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'Статус удалённого узла'
                )
            )
        )

        remote_i2p_node_status_raw = (
            'Оффлайн'
        )

        remote_i2p_node_status_value_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    remote_i2p_node_status_raw
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
            local_i2p_node_sam_session_incoming_data_connection_status_key_label,
            2, 0, 1, 1
        )

        info_layout.addWidget(
            local_i2p_node_sam_session_incoming_data_connection_status_value_label,
            2, 1, 1, 1
        )

        info_layout.addWidget(
            local_i2p_node_sam_session_outgoing_data_connection_status_key_label,
            3, 0, 1, 1
        )

        info_layout.addWidget(
            local_i2p_node_sam_session_outgoing_data_connection_status_value_label,
            3, 1, 1, 1
        )

        info_layout.addWidget(
            remote_i2p_node_status_key_label,
            4, 0, 1, 1
        )

        info_layout.addWidget(
            remote_i2p_node_status_value_label,
            4, 1, 1, 1
        )

        window_layout.addLayout(
            info_layout
        )

        # Filling conversation layout

        conversation_layout = (
            QGridLayout()
        )

        conversation_text_edit = (
            QTextEdit()
        )

        conversation_text_edit.setPlaceholderText(
            'Диалог с собеседником'
        )

        conversation_text_edit.setReadOnly(
            True
        )

        message_send_button = (
            QPushButton()
        )

        message_send_button.setText(
            'Отправить сообщение'
        )

        message_send_button.clicked.connect(  # noqa
            self.__on_message_send_button_clicked
        )

        message_text_edit = (
            QTextEdit()
        )

        message_text_edit.setPlaceholderText(
            'Введите сообщение...'
        )

        # TODO: on text changed call handler && activate or deactivate message send button

        conversation_layout.addWidget(
            conversation_text_edit,
            0, 0, 1, 8
        )

        conversation_layout.setRowMinimumHeight(  # TODO: make this better
            0,
            10000
        )

        conversation_layout.addWidget(
            message_text_edit,
            1, 0, 1, 7
        )

        conversation_layout.addWidget(
            message_send_button,
            1, 7, 1, 1
        )

        window_layout.addLayout(
            conversation_layout
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

        self.__last_remote_i2p_node_ping_timestamp_ms = (
            None
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

        self.__local_i2p_node_message_raw_data_by_id_map: (
            typing.Dict[
                int,
                typing.Dict
            ]
        ) = {}

        self.__local_i2p_node_pending_message_raw_data_by_id_map: (
            typing.Dict[
                int,
                typing.Dict
            ]
        ) = {}

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

        self.__local_i2p_node_sam_session_incoming_data_connection: (
            typing.Optional[
                _Connection
            ]
        ) = None

        self.__local_i2p_node_sam_session_incoming_data_connection_status_key_label = (
            local_i2p_node_sam_session_incoming_data_connection_status_key_label
        )

        self.__local_i2p_node_sam_session_incoming_data_connection_status_raw = (
            local_i2p_node_sam_session_incoming_data_connection_status_raw
        )

        self.__local_i2p_node_sam_session_incoming_data_connection_status_value_label = (
            local_i2p_node_sam_session_incoming_data_connection_status_value_label
        )

        self.__local_i2p_node_sam_session_name = (
            self.__generate_i2p_node_sam_session_name()
        )

        self.__local_i2p_node_sam_session_outgoing_data_connection: (
            typing.Optional[
                _Connection
            ]
        ) = None

        self.__local_i2p_node_sam_session_outgoing_data_connection_status_key_label = (
            local_i2p_node_sam_session_outgoing_data_connection_status_key_label
        )

        self.__local_i2p_node_sam_session_outgoing_data_connection_status_raw = (
            local_i2p_node_sam_session_outgoing_data_connection_status_raw
        )

        self.__local_i2p_node_sam_session_outgoing_data_connection_status_value_label = (
            local_i2p_node_sam_session_outgoing_data_connection_status_value_label
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

        self.__local_i2p_node_sam_session_update_lock = (
            asyncio.Lock()
        )

        self.__message_send_button = (
            message_send_button
        )

        self.__message_text_edit = (
            message_text_edit
        )

        self.__remote_i2p_node_address_line_edit = (
            remote_i2p_node_address_line_edit
        )

        self.__remote_i2p_node_address_raw: (
            typing.Optional[
                str
            ]
        ) = None

        self.__remote_i2p_node_message_raw_data_by_id_map: (
            typing.Dict[
                int,
                typing.Dict
            ]
        ) = {}

        self.__remote_i2p_node_status_key_label = (
            remote_i2p_node_status_key_label
        )

        self.__remote_i2p_node_status_raw = (
            remote_i2p_node_status_raw
        )

        self.__remote_i2p_node_status_value_label = (
            remote_i2p_node_status_value_label
        )

        asyncio.create_task(
            self.__on_local_i2p_node_sam_ip_address_line_edit_text_changed_ex()
        )

        asyncio.create_task(
            self.__on_local_i2p_node_sam_port_line_edit_text_changed_ex()
        )

        asyncio.create_task(
            self.__on_remote_i2p_node_address_line_edit_text_changed_ex()
        )

        self.__update_local_i2p_node_address()

    async def start_local_i2p_node_sam_session_incoming_data_connection_creation_loop(
            self
    ) -> None:
        while True:
            if self.__local_i2p_node_sam_session_control_connection is None:
                await (
                    self.__local_i2p_node_sam_session_creation_event.wait()
                )

                assert (
                    self.__local_i2p_node_sam_session_control_connection is not None
                ), None

            local_i2p_node_sam_ip_address = (
                self.__local_i2p_node_sam_ip_address
            )

            if local_i2p_node_sam_ip_address is None:
                await (
                    self.__update_local_i2p_node_sam_session_incoming_data_connection_status(
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
                    self.__update_local_i2p_node_sam_session_incoming_data_connection_status(
                        'Невозможно создать без I2P SAM порта'
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

            try:
                (
                    local_i2p_node_sam_session_incoming_data_reader,
                    local_i2p_node_sam_session_incoming_data_writer
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
            except i2plib.exceptions.InvalidId:
                await (
                    self.__update_local_i2p_node_sam_session_incoming_data_connection_status(
                        'Ошибка: сессии не существует'
                    )
                )

                await (
                    self.__close_local_i2p_node_sam_session_control_connection()
                )

                await (
                    self.__close_local_i2p_node_sam_session_incoming_data_connection()
                )

                local_i2p_node_sam_session_incoming_data_connection = (  # noqa
                    None
                )

                await (
                    self.__update_local_i2p_node_sam_session()
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

            self.__local_i2p_node_sam_session_incoming_data_connection = (
                local_i2p_node_sam_session_incoming_data_connection
            ) = (
                _Connection(
                    local_i2p_node_sam_session_incoming_data_reader,
                    local_i2p_node_sam_session_incoming_data_writer
                )
            )

            await (
                self.__update_local_i2p_node_sam_session_incoming_data_connection_status(
                    'Прослушивание...'
                )
            )

            remote_i2p_node_destination_bytes = (
                await (
                    local_i2p_node_sam_session_incoming_data_reader.readline()
                )
            )

            if not remote_i2p_node_destination_bytes:
                # Connection was closed

                await (
                    self.__close_local_i2p_node_sam_session_incoming_data_connection()
                )

                local_i2p_node_sam_session_incoming_data_connection = (  # noqa
                    None
                )

                await (
                    self.__update_local_i2p_node_sam_session_incoming_data_connection_status(
                        'Прервано'
                    )
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

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

            logger.info(
                'New client'
                f' with remote I2P Node address {remote_i2p_node_address_raw!r}'
                ' was connected!'
            )

            settled_remote_i2p_node_address_raw = (
                self.__remote_i2p_node_address_raw
            )

            if settled_remote_i2p_node_address_raw is None:
                await (
                    self.__update_local_i2p_node_sam_session_incoming_data_connection_status(
                        'Невозможно создать без I2P адреса удалённого узла'
                    )
                )

                await (
                    self.__close_local_i2p_node_sam_session_incoming_data_connection()
                )

                local_i2p_node_sam_session_incoming_data_connection = (  # noqa
                    None
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

            is_settled_remote_i2p_node_address_raw_valid = (
                self.__is_i2p_node_address_raw_valid(
                    settled_remote_i2p_node_address_raw
                )
            )

            if not is_settled_remote_i2p_node_address_raw_valid:
                await (
                    self.__update_local_i2p_node_sam_session_incoming_data_connection_status(
                        'I2P адрес удалённого узла некорректен'
                    )
                )

                await (
                    self.__close_local_i2p_node_sam_session_incoming_data_connection()
                )

                local_i2p_node_sam_session_incoming_data_connection = (  # noqa
                    None
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

            if (
                    remote_i2p_node_address_raw !=
                    settled_remote_i2p_node_address_raw
            ):
                await (
                    self.__update_local_i2p_node_sam_session_incoming_data_connection_status(
                        'I2P адрес подключенного клиента не соответствует прописанному'
                    )
                )

                await (
                    self.__close_local_i2p_node_sam_session_incoming_data_connection()
                )

                local_i2p_node_sam_session_incoming_data_connection = (  # noqa
                    None
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

            await (
                self.__update_local_i2p_node_sam_session_incoming_data_connection_status(
                    'Создано'
                )
            )

            tasks = (
                asyncio.ensure_future(
                    self.__start_local_i2p_node_sam_session_data_connection_pinging_loop(
                        local_i2p_node_sam_session_incoming_data_connection
                    )
                ),

                asyncio.ensure_future(
                    self.__start_local_i2p_node_sam_session_data_connection_sending_loop(
                        local_i2p_node_sam_session_incoming_data_connection
                    )
                ),

                asyncio.ensure_future(
                    self.__start_local_i2p_node_sam_session_data_connection_receiving_loop(
                        local_i2p_node_sam_session_incoming_data_connection
                    )
                )
            )

            try:
                await (
                    asyncio.gather(
                        *tasks
                    )
                )
            except BrokenPipeError:
                for task in tasks:
                    task.cancel()

                await (
                    self.__close_local_i2p_node_sam_session_incoming_data_connection()
                )

                local_i2p_node_sam_session_incoming_data_connection = (  # noqa
                    None
                )

                await (
                    self.__update_local_i2p_node_sam_session_incoming_data_connection_status(
                        'Прервано'
                    )
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

    @staticmethod
    def __send_ack_raw_data(
            connection: (
                _Connection
            ),

            message_id: int
    ) -> None:
        raw_data = {
            'message_id': (
                message_id
            ),

            'type': (
                'ack'
            )
        }

        connection.send_raw_data(
            raw_data
        )

    @staticmethod
    def __send_message_raw_data(
            connection: (
                _Connection
            ),

            message_id: int,

            message_raw_data: (
                typing.Dict
            )
    ) -> None:
        raw_data = (
            message_raw_data.copy()
        )

        raw_data.update({
            'id': (
                message_id
            ),

            'type': (
                'message'
            )
        })

        connection.send_raw_data(
            raw_data
        )

    @staticmethod
    async def __start_local_i2p_node_sam_session_data_connection_pinging_loop(
            connection: (
                _Connection
            )
    ) -> None:
        while True:
            connection.send_raw_data({
                'type': (
                    'ping'
                )
            })

            await (
                asyncio.sleep(
                    5.0  # s
                )
            )

    async def __start_local_i2p_node_sam_session_data_connection_sending_loop(
            self,

            connection: (
                _Connection
            )
    ) -> None:
        local_i2p_node_pending_message_raw_data_by_id_map = (
            self.__local_i2p_node_pending_message_raw_data_by_id_map
        )

        while True:
            for pending_message_id in (
                    sorted(
                        local_i2p_node_pending_message_raw_data_by_id_map
                    )
            ):
                pending_message_raw_data = (
                    local_i2p_node_pending_message_raw_data_by_id_map[
                        pending_message_id
                    ]
                )

                self.__send_message_raw_data(
                    connection,
                    pending_message_id,
                    pending_message_raw_data
                )

            await (
                asyncio.sleep(
                    1.0  # s
                )
            )

    async def __start_local_i2p_node_sam_session_data_connection_receiving_loop(
            self,

            connection: (
                _Connection
            )
    ) -> None:
        local_i2p_node_pending_message_raw_data_by_id_map = (
            self.__local_i2p_node_pending_message_raw_data_by_id_map
        )

        remote_i2p_node_message_raw_data_by_id_map = (
            self.__remote_i2p_node_message_raw_data_by_id_map
        )

        while True:
            raw_data = (
                await (
                    connection.read_raw_data()
                )
            )

            if raw_data is None:
                # Connection was closed

                raise (
                    BrokenPipeError
                )

            raw_data_type: (
                typing.Optional[
                    str
                ]
            ) = (
                raw_data.pop(
                    'type',
                    None
                )
            )

            if raw_data_type is None:
                logger.warning(
                    ': Raw data without type'
                    f': {raw_data}'
                )

                continue

            if (
                    raw_data_type ==
                    'ack'
            ):
                ack_raw_data = (
                    raw_data
                )

                message_id: (
                    typing.Optional[
                        int
                    ]
                ) = (
                    ack_raw_data.pop(
                        'message_id',
                        None
                    )
                )

                if message_id is None:
                    logger.warning(
                        ': ACK raw data without message ID field'
                        f': {ack_raw_data}'
                    )

                    continue
                elif (
                        type(
                            message_id
                        ) is not

                        int
                ):
                    logger.warning(
                        ': ACK raw data have incorrect message ID field type'
                        f': {ack_raw_data}'
                    )

                    continue

                (
                    local_i2p_node_pending_message_raw_data_by_id_map.pop(
                        message_id,
                        None
                    )
                )

                self.__update_conversation()
            elif (
                    raw_data_type ==
                    'ping'
            ):
                self.__last_remote_i2p_node_ping_timestamp_ms = (
                    get_aware_current_timestamp_ms()
                )
            elif (
                    raw_data_type ==
                    'message'
            ):
                message_raw_data = (
                    raw_data
                )

                message_id: (
                    typing.Optional[
                        int
                    ]
                ) = (
                    message_raw_data.pop(
                        'id',
                        None
                    )
                )

                if message_id is None:
                    logger.warning(
                        ': Message raw data without ID field'
                        f': {message_raw_data}'
                    )

                    continue
                elif (
                        type(
                            message_id
                        ) is not

                        int
                ):
                    logger.warning(
                        ': Message raw data have incorrect ID field type'
                        f': {message_raw_data}'
                    )

                    continue
                # TODO: check message_id >= 0

                if self.__local_i2p_node_sam_session_control_connection is not None:
                    for data_connection in (
                            self.__local_i2p_node_sam_session_incoming_data_connection,
                            self.__local_i2p_node_sam_session_outgoing_data_connection
                    ):
                        if data_connection is not None:
                            self.__send_ack_raw_data(
                                data_connection,
                                message_id
                            )

                            break

                if (
                        message_id in
                        remote_i2p_node_message_raw_data_by_id_map
                ):
                    continue

                message_text: (
                    typing.Optional[
                        str
                    ]
                ) = (
                    message_raw_data.pop(
                        'text',
                        None
                    )
                )

                if message_text is None:
                    logger.warning(
                        ': Message raw data without text field'
                        f': {message_raw_data}'
                    )
                elif (
                        type(
                            message_text
                        ) is not

                        str
                ):
                    logger.warning(
                        ': Message raw data have incorrect text field type'
                        f': {message_raw_data}'
                    )

                    continue
                # TODO: check text is not empty (for MVP)

                if message_raw_data:
                    logger.warning(
                        'Message raw data has extra fields'
                        f': {message_raw_data}'
                    )

                message_raw_data = {
                    'text': (
                        message_text
                    ),

                    'timestamp_ms': (
                        get_aware_current_timestamp_ms()
                    )
                }

                (
                    remote_i2p_node_message_raw_data_by_id_map[
                        message_id
                    ]
                ) = message_raw_data

                self.__update_conversation()

    async def start_local_i2p_node_sam_session_outgoing_data_connection_creation_loop(
            self
    ) -> None:
        while True:
            if self.__local_i2p_node_sam_session_control_connection is None:
                await (
                    self.__local_i2p_node_sam_session_creation_event.wait()
                )

                assert (
                    self.__local_i2p_node_sam_session_control_connection is not None
                ), None

            local_i2p_node_sam_ip_address = (
                self.__local_i2p_node_sam_ip_address
            )

            if local_i2p_node_sam_ip_address is None:
                await (
                    self.__update_local_i2p_node_sam_session_outgoing_data_connection_status(
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
                    self.__update_local_i2p_node_sam_session_outgoing_data_connection_status(
                        'Невозможно создать без I2P SAM порта'
                    )
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

            remote_i2p_node_address_raw = (
                self.__remote_i2p_node_address_raw
            )

            if remote_i2p_node_address_raw is None:
                await (
                    self.__update_local_i2p_node_sam_session_outgoing_data_connection_status(
                        'Невозможно создать без I2P адреса удалённого узла'
                    )
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

            is_remote_i2p_node_address_raw_valid = (
                self.__is_i2p_node_address_raw_valid(
                    remote_i2p_node_address_raw
                )
            )

            if not is_remote_i2p_node_address_raw_valid:
                await (
                    self.__update_local_i2p_node_sam_session_outgoing_data_connection_status(
                        'I2P адрес удалённого узла некорректен'
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

            await (
                self.__update_local_i2p_node_sam_session_outgoing_data_connection_status(
                    'Попытка создания...'
                )
            )

            try:
                (
                    local_i2p_node_sam_session_outgoing_data_reader,
                    local_i2p_node_sam_session_outgoing_data_writer
                ) = (
                    await (
                        i2plib.stream_connect(
                            destination=(
                                remote_i2p_node_address_raw
                            ),

                            session_name=(
                                self.__local_i2p_node_sam_session_name
                            ),

                            sam_address=(
                                local_i2p_node_sam_ip_address_and_port_pair
                            )
                        )
                    )
                )
            except i2plib.exceptions.CantReachPeer:
                await (
                    self.__update_local_i2p_node_sam_session_outgoing_data_connection_status(
                        'Не удалось подключиться к удалённому узлу'
                    )
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue
            except i2plib.exceptions.InvalidId:
                await (
                    self.__update_local_i2p_node_sam_session_outgoing_data_connection_status(
                        'Ошибка: сессии не существует'
                    )
                )

                await (
                    self.__close_local_i2p_node_sam_session_control_connection()
                )

                await (
                    self.__update_local_i2p_node_sam_session()
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue
            except i2plib.exceptions.InvalidKey:
                await (
                    self.__update_local_i2p_node_sam_session_outgoing_data_connection_status(
                        'Ошибка: некорректный I2P адрес удалённого узла'
                    )
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

            self.__local_i2p_node_sam_session_outgoing_data_connection = (
                local_i2p_node_sam_session_outgoing_data_connection
            ) = (
                _Connection(
                    local_i2p_node_sam_session_outgoing_data_reader,
                    local_i2p_node_sam_session_outgoing_data_writer
                )
            )

            await (
                self.__update_local_i2p_node_sam_session_outgoing_data_connection_status(
                    'Создано'
                )
            )

            logger.info(
                'Successfully connected to client'
                f' with remote I2P Node address {remote_i2p_node_address_raw!r}'
            )

            tasks = (
                asyncio.ensure_future(
                    self.__start_local_i2p_node_sam_session_data_connection_pinging_loop(
                        local_i2p_node_sam_session_outgoing_data_connection
                    )
                ),

                asyncio.ensure_future(
                    self.__start_local_i2p_node_sam_session_data_connection_sending_loop(
                        local_i2p_node_sam_session_outgoing_data_connection
                    )
                ),

                asyncio.ensure_future(
                    self.__start_local_i2p_node_sam_session_data_connection_receiving_loop(
                        local_i2p_node_sam_session_outgoing_data_connection
                    )
                )
            )

            try:
                await (
                    asyncio.gather(
                        *tasks
                    )
                )
            except BrokenPipeError:
                for task in tasks:
                    task.cancel()

                await (
                    self.__close_local_i2p_node_sam_session_outgoing_data_connection()
                )

                local_i2p_node_sam_session_outgoing_data_connection = (  # noqa
                    None
                )

                await (
                    self.__update_local_i2p_node_sam_session_outgoing_data_connection_status(
                        'Прервано'
                    )
                )

                await (  # TODO: make this better
                    asyncio.sleep(
                        1.0
                    )
                )

                continue

    async def start_remote_i2p_node_status_update_loop(
            self
    ) -> None:
        while True:
            last_remote_i2p_node_ping_timestamp_ms = (
                self.__last_remote_i2p_node_ping_timestamp_ms
            )

            new_remote_i2p_node_status_raw: str

            if last_remote_i2p_node_ping_timestamp_ms is not None:
                current_timestamp_ms = (
                    get_aware_current_timestamp_ms()
                )

                delta_time_ms = (
                    current_timestamp_ms -
                    last_remote_i2p_node_ping_timestamp_ms
                )

                if (
                        delta_time_ms <
                        1000  # ms
                ):
                    new_remote_i2p_node_status_raw = (
                        f'Онлайн ({delta_time_ms} мс)'
                    )
                else:
                    delta_time_seconds = (
                        delta_time_ms //
                        1000  # ms
                    )

                    new_remote_i2p_node_status_raw = (
                        f'Онлайн ({delta_time_seconds} с)'
                    )
            else:
                new_remote_i2p_node_status_raw = (
                    'Оффлайн'
                )

            await (
                self.__update_remote_i2p_node_status(
                    new_remote_i2p_node_status_raw
                )
            )

            await (
                asyncio.sleep(
                    1.0  # s
                )
            )

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

    async def __close_local_i2p_node_sam_session_incoming_data_connection(
            self
    ) -> None:
        local_i2p_node_sam_session_incoming_data_connection = (
            self.__local_i2p_node_sam_session_incoming_data_connection
        )

        if local_i2p_node_sam_session_incoming_data_connection is not None:
            local_i2p_node_sam_session_incoming_data_connection.close()

            self.__local_i2p_node_sam_session_incoming_data_connection = (
                local_i2p_node_sam_session_incoming_data_connection  # noqa
            ) = None

    async def __close_local_i2p_node_sam_session_outgoing_data_connection(
            self
    ) -> None:
        local_i2p_node_sam_session_outgoing_data_connection = (
            self.__local_i2p_node_sam_session_outgoing_data_connection
        )

        if local_i2p_node_sam_session_outgoing_data_connection is not None:
            local_i2p_node_sam_session_outgoing_data_connection.close()

            self.__local_i2p_node_sam_session_outgoing_data_connection = (
                local_i2p_node_sam_session_outgoing_data_connection  # noqa
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

    @staticmethod
    def __is_i2p_node_address_raw_valid(
            i2p_node_address_raw: str
    ) -> bool:
        return (
            i2p_node_address_raw.endswith(
                '.i2p'
            )
        )

    @asyncSlot()
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
            logger.info(
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

    @asyncSlot()
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
                logger.info(
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

    @asyncSlot()
    async def __on_message_send_button_clicked(
            self
    ) -> None:
        message_text_edit = (
            self.__message_text_edit
        )

        message_text = (
            message_text_edit.toPlainText().strip()
        )

        if not message_text:
            return

        local_i2p_node_message_raw_data_by_id_map = (
            self.__local_i2p_node_message_raw_data_by_id_map
        )

        message_id: int

        if local_i2p_node_message_raw_data_by_id_map:
            message_id = (
                max(
                    local_i2p_node_message_raw_data_by_id_map
                ) +

                1
            )
        else:
            message_id = 0

        (
            local_i2p_node_message_raw_data_by_id_map[
                message_id
            ]
        ) = {
            'text': (
                message_text
            ),

            'timestamp_ms': (
                get_aware_current_timestamp_ms()
            )
        }

        pending_message_raw_data = (
            self.__local_i2p_node_pending_message_raw_data_by_id_map[
                message_id
            ]
        ) = {
            'text': (
                message_text
            )
        }

        self.__update_conversation()

        if self.__local_i2p_node_sam_session_control_connection is not None:
            for data_connection in (
                    self.__local_i2p_node_sam_session_incoming_data_connection,
                    self.__local_i2p_node_sam_session_outgoing_data_connection
            ):
                if data_connection is not None:
                    self.__send_message_raw_data(
                        data_connection,
                        message_id,
                        pending_message_raw_data
                    )

                    break

        message_text_edit.setText(
            ''
        )

        # TODO: update message sending button active flag

    @asyncSlot()
    async def __on_remote_i2p_node_address_line_edit_text_changed(
            self
    ) -> None:
        await (
            self.__on_remote_i2p_node_address_line_edit_text_changed_ex()
        )

    async def __on_remote_i2p_node_address_line_edit_text_changed_ex(
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

        is_new_remote_i2p_node_address_raw_valid = (
            self.__is_i2p_node_address_raw_valid(
                new_remote_i2p_node_address_raw
            )
        )

        if is_new_remote_i2p_node_address_raw_valid:  # TODO: check by regexp match
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

        await (
            self.__close_local_i2p_node_sam_session_outgoing_data_connection()
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

    def __update_conversation(
            self
    ) -> None:
        conversation_message_raw_data_list_by_timestamp_ms_map = (
            defaultdict(
                list
            )
        )

        local_i2p_node_message_raw_data_by_id_map = (
            self.__local_i2p_node_message_raw_data_by_id_map
        )

        local_i2p_node_pending_message_raw_data_by_id_map = (
            self.__local_i2p_node_pending_message_raw_data_by_id_map
        )

        remote_i2p_node_message_raw_data_by_id_map = (
            self.__remote_i2p_node_message_raw_data_by_id_map
        )

        for is_own_messages, i2p_node_message_raw_data_by_id_map in (
                (
                    True,
                    local_i2p_node_message_raw_data_by_id_map
                ),

                (
                    False,
                    remote_i2p_node_message_raw_data_by_id_map
                )
        ):
            for message_id, message_raw_data in (
                    i2p_node_message_raw_data_by_id_map.items()
            ):
                message_raw_data = (
                    message_raw_data.copy()
                )

                (
                    message_raw_data[
                        'is_own'
                    ]
                ) = is_own_messages

                if is_own_messages:
                    is_message_delivered = (
                        message_id not in
                        local_i2p_node_pending_message_raw_data_by_id_map
                    )

                    (
                        message_raw_data[
                            'is_delivered'
                        ]
                    ) = is_message_delivered

                timestamp_ms: int = (
                    message_raw_data[
                        'timestamp_ms'
                    ]
                )

                conversation_message_raw_data_list = (
                    conversation_message_raw_data_list_by_timestamp_ms_map[
                        timestamp_ms
                    ]
                )

                conversation_message_raw_data_list.append(
                    message_raw_data
                )

        conversation_text_edit = (
            self.__conversation_text_edit
        )

        new_conversation_html_io = (
            io.StringIO()
        )

        for message_idx, timestamp_ms in (
                enumerate(
                    sorted(
                        conversation_message_raw_data_list_by_timestamp_ms_map
                    )
                )
        ):
            # if message_idx:
            #     new_conversation_html_io.write(
            #         '<br>' '\n'
            #     )

            new_conversation_html_io.write(
                f'<div id="message_{message_idx}">'
            )

            message_datetime = (
                datetime.fromtimestamp(
                    (
                        timestamp_ms //
                        1000  # ms
                    ),

                    tz=(
                        timezone.utc
                    )
                )
            )

            new_conversation_html_io.write(
                f'[{message_datetime.astimezone().isoformat()}]',  # TODO
            )

            conversation_message_raw_data_list = (
                conversation_message_raw_data_list_by_timestamp_ms_map.get(
                    timestamp_ms
                )
            )

            assert (
                conversation_message_raw_data_list is not None
            ), None

            for conversation_message_raw_data in (
                    conversation_message_raw_data_list
            ):
                is_own_message: bool = (
                    conversation_message_raw_data[
                        'is_own'
                    ]
                )

                if is_own_message:
                    new_conversation_html_io.write(
                        f'[Вы]'
                    )

                    is_message_delivered: bool = (
                        conversation_message_raw_data[
                            'is_delivered'
                        ]
                    )

                    if is_message_delivered:
                        new_conversation_html_io.write(
                            '[✅ Доставлено]'
                        )
                    else:
                        new_conversation_html_io.write(
                            '[⌛ Ожидание доставки...]',
                        )
                else:
                    new_conversation_html_io.write(
                        f'[Собеседник]'
                    )

                conversation_message_text = (
                    conversation_message_raw_data[
                        'text'
                    ]
                )

                new_conversation_html_io.write(
                    f': {conversation_message_text}'
                )

            new_conversation_html_io.write(
                '</div>'
            )

        new_conversation_html_io.seek(
            0
        )

        new_conversation_html = (
            new_conversation_html_io.read().strip()
        )

        old_conversation_html = (
            conversation_text_edit.toHtml().strip()
        )

        if (
                new_conversation_html ==
                old_conversation_html
        ):
            return

        conversation_text_edit.setHtml(
            new_conversation_html
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
                    self.__close_local_i2p_node_sam_session_incoming_data_connection()
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
                    self.__close_local_i2p_node_sam_session_incoming_data_connection()
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
                    self.__close_local_i2p_node_sam_session_incoming_data_connection()
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

            local_i2p_node_sam_ip_address_and_port_pair = (
                str(
                    local_i2p_node_sam_ip_address
                ),

                local_i2p_node_sam_port
            )

            while True:
                await (
                    self.__update_local_i2p_node_sam_session_status(
                        'Попытка создания...'
                    )
                )

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

                    await (
                        self.__update_local_i2p_node_sam_session_status(
                            'Тайм-аут'
                        )
                    )

                    await (
                        asyncio.sleep(
                            1.0  # s
                        )
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

    async def __update_local_i2p_node_sam_session_incoming_data_connection_status(
            self,

            new_local_i2p_node_sam_session_incoming_data_connection_status_raw: str
    ) -> None:
        local_i2p_node_sam_session_incoming_data_connection_status_value_label = (
            self.__local_i2p_node_sam_session_incoming_data_connection_status_value_label
        )

        old_local_i2p_node_sam_session_incoming_data_connection_status_raw = (
            local_i2p_node_sam_session_incoming_data_connection_status_value_label.text().strip()
        )

        if (
                old_local_i2p_node_sam_session_incoming_data_connection_status_raw is not None and

                (
                    new_local_i2p_node_sam_session_incoming_data_connection_status_raw ==
                    old_local_i2p_node_sam_session_incoming_data_connection_status_raw
                )
        ):
            return

        local_i2p_node_sam_session_incoming_data_connection_status_value_label.setText(
            new_local_i2p_node_sam_session_incoming_data_connection_status_raw
        )

        logger.info(
            'New incoming data connection status'
            f': {new_local_i2p_node_sam_session_incoming_data_connection_status_raw!r}'
        )

        self.__local_i2p_node_sam_session_incoming_data_connection_status_raw = (
            new_local_i2p_node_sam_session_incoming_data_connection_status_raw
        )

    async def __update_local_i2p_node_sam_session_outgoing_data_connection_status(
            self,

            new_local_i2p_node_sam_session_outgoing_data_connection_status_raw: str
    ) -> None:
        local_i2p_node_sam_session_outgoing_data_connection_status_value_label = (
            self.__local_i2p_node_sam_session_outgoing_data_connection_status_value_label
        )

        old_local_i2p_node_sam_session_outgoing_data_connection_status_raw = (
            local_i2p_node_sam_session_outgoing_data_connection_status_value_label.text().strip()
        )

        if (
                old_local_i2p_node_sam_session_outgoing_data_connection_status_raw is not None and

                (
                    new_local_i2p_node_sam_session_outgoing_data_connection_status_raw ==
                    old_local_i2p_node_sam_session_outgoing_data_connection_status_raw
                )
        ):
            return

        local_i2p_node_sam_session_outgoing_data_connection_status_value_label.setText(
            new_local_i2p_node_sam_session_outgoing_data_connection_status_raw
        )

        logger.info(
            'New outgoing data connection status'
            f': {new_local_i2p_node_sam_session_outgoing_data_connection_status_raw!r}'
        )

        self.__local_i2p_node_sam_session_outgoing_data_connection_status_raw = (
            new_local_i2p_node_sam_session_outgoing_data_connection_status_raw
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

        logger.info(
            'New session status'
            f': {new_local_i2p_node_sam_session_status_raw!r}'
        )

        self.__local_i2p_node_sam_session_status_raw = (
            new_local_i2p_node_sam_session_status_raw
        )

    async def __update_remote_i2p_node_status(
            self,

            new_remote_i2p_node_status_raw: str
    ) -> None:
        remote_i2p_node_status_value_label = (
            self.__remote_i2p_node_status_value_label
        )

        old_remote_i2p_node_status_raw = (
            remote_i2p_node_status_value_label.text().strip()
        )

        if (
                old_remote_i2p_node_status_raw is not None and

                (
                    new_remote_i2p_node_status_raw ==
                    old_remote_i2p_node_status_raw
                )
        ):
            return

        remote_i2p_node_status_value_label.setText(
            new_remote_i2p_node_status_raw
        )

        logger.info(
            'New remote I2P node status'
            f': {new_remote_i2p_node_status_raw!r}'
        )

        self.__remote_i2p_node_status_raw = (
            new_remote_i2p_node_status_raw
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
            # window.start_local_i2p_node_sam_session_control_connection_creation_loop(),
            window.start_local_i2p_node_sam_session_incoming_data_connection_creation_loop(),
            window.start_local_i2p_node_sam_session_outgoing_data_connection_creation_loop(),
            window.start_remote_i2p_node_status_update_loop(),
            application_close_event.wait()
        )
    )


def main() -> None:
    logging_handlers = [
        _CustomStreamHandler()
    ]

    logging_level: str

    if _IS_DEBUG:
        logging_handlers.append(
            logging.FileHandler(
                f'log.log',

                encoding=(
                    'utf-8'
                )
            )
        )

        logging_level = (
            logging.DEBUG
        )
    else:
        logging_level = (
            logging.INFO
        )

    logging.basicConfig(
        encoding=(
            'utf-8'
        ),

        format=(
            '[%(levelname)s]'
            '[%(asctime)s]'
            '[%(name)s]'
            ': %(message)s'
        ),

        handlers=(
            logging_handlers
        ),

        level=(
            logging_level
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
