import asyncio
import codecs
import logging

import sys
import typing

from ipaddress import (
    ip_address,
    IPv4Address,
    IPv6Address
)

import i2plib
import orjson

from PyQt6.QtCore import (
    Qt
)

from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLineEdit,
    QMainWindow,
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

_I2P_SAM_SESSION_NAME = (
    'session'
)

class MainWindow(QMainWindow):
    __slots__ = (
        '__config_raw_data',
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
        '__local_i2p_node_sam_session_reader',
        '__local_i2p_node_sam_session_writer',
        '__remote_i2p_node_address_line_edit',
        '__remote_i2p_node_address_raw',
        '__remote_i2p_node_port',
        '__remote_i2p_node_port_raw',
        '__remote_i2p_node_port_line_edit'
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

        remote_i2p_node_port_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'Порт удалённого узла'
                )
            )
        )

        remote_i2p_node_port_line_edit = (
            QLineEdit()
        )

        remote_i2p_node_port_raw: (
            typing.Optional[
                str
            ]
        ) = (
            config_raw_data.get(
                'remote_i2p_node_port_raw'
            )
        )

        if remote_i2p_node_port_raw:
            remote_i2p_node_port_line_edit.setText(
                remote_i2p_node_port_raw
            )

        remote_i2p_node_port_line_edit.textChanged.connect(  # noqa
            self.__on_remote_i2p_node_port_line_edit_text_changed
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
            2, 0, 1, 1
        )

        functionality_layout.addWidget(
            remote_i2p_node_port_label,
            2, 1, 1, 1
        )

        functionality_layout.addWidget(
            remote_i2p_node_address_line_edit,
            3, 0, 1, 1
        )

        functionality_layout.addWidget(
            remote_i2p_node_port_line_edit,
            3, 1, 1, 1
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

        info_layout.addWidget(
            local_i2p_node_address_key_label,
            0, 0, 1, 1
        )

        info_layout.addWidget(
            local_i2p_node_address_value_label,
            0, 1, 1, 1
        )

        window_layout.addLayout(
            info_layout
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

        self.__local_i2p_node_sam_session_reader: (
            typing.Optional[
                asyncio.StreamReader
            ]
        ) = None

        self.__local_i2p_node_sam_session_writer: (
            typing.Optional[
                asyncio.StreamWriter
            ]
        ) = None

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

        self.__remote_i2p_node_port_line_edit = (
            remote_i2p_node_port_line_edit
        )

        self.__remote_i2p_node_port_raw: (
            typing.Optional[
                str
            ]
        ) = None

        asyncio.create_task(
            self.__on_local_i2p_node_sam_ip_address_line_edit_text_changed_ex()
        )

        asyncio.create_task(
            self.__on_local_i2p_node_sam_port_line_edit_text_changed_ex()
        )

        self.__on_remote_i2p_node_address_line_edit_text_changed()
        self.__on_remote_i2p_node_port_line_edit_text_changed()

        self.__update_local_i2p_node_address()

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

    async def __close_local_i2p_node_sam_session(
            self
    ) -> None:
        local_i2p_node_sam_session_reader = (
            self.__local_i2p_node_sam_session_reader
        )

        if local_i2p_node_sam_session_reader is not None:
            self.__local_i2p_node_sam_session_reader = (
                local_i2p_node_sam_session_reader  # noqa
            ) = None

        local_i2p_node_sam_session_writer = (
            self.__local_i2p_node_sam_session_writer
        )

        if local_i2p_node_sam_session_writer is not None:
            local_i2p_node_sam_session_writer.close()

            self.__local_i2p_node_sam_session_writer = (
                local_i2p_node_sam_session_writer  # noqa
            ) = None

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

    def __on_remote_i2p_node_port_line_edit_text_changed(
            self
    ) -> None:
        remote_i2p_node_port_line_edit = (
            self.__remote_i2p_node_port_line_edit
        )

        new_remote_i2p_node_port_raw = (
            remote_i2p_node_port_line_edit.text().strip()
        )

        old_remote_i2p_node_port_raw = (
            self.__remote_i2p_node_port_raw
        )

        if (
                old_remote_i2p_node_port_raw is not None and

                (
                    new_remote_i2p_node_port_raw ==
                    old_remote_i2p_node_port_raw
                )
        ):
            return

        self.__remote_i2p_node_port_raw = (
            new_remote_i2p_node_port_raw
        )

        (
            self.__config_raw_data[
                'remote_i2p_node_port_raw'
            ]
        ) = new_remote_i2p_node_port_raw

        self.__save_config()

        new_remote_i2p_node_port: (
            typing.Optional[
                int
            ]
        )

        if new_remote_i2p_node_port_raw.isdigit():
            try:
                new_remote_i2p_node_port = (
                    int(
                        new_remote_i2p_node_port_raw
                    )
                )

                if not (
                        0 <
                        new_remote_i2p_node_port <

                        (
                            1 <<
                            16
                        )
                ):
                    new_remote_i2p_node_port = (
                        None
                    )
            except ValueError:
                print(
                    f'Could not parse port {new_remote_i2p_node_port_raw!r}'
                )

                new_remote_i2p_node_port = (
                    None
                )
        else:
            new_remote_i2p_node_port = (
                None
            )

        self.__remote_i2p_node_port = (
            new_remote_i2p_node_port
        )

        if new_remote_i2p_node_port is not None:
            remote_i2p_node_port_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(0, 255, 0, 0.25);'
                ' selection-background-color: rgba(0, 255, 0, 0.5);'
                ' }'
            )
        else:
            remote_i2p_node_port_line_edit.setStyleSheet(
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
        if self.__local_i2p_node_sam_session_reader is not None:
            assert (
                self.__local_i2p_node_sam_session_writer is not None
            ), None

            return

        local_i2p_node_destination = (
            self.__local_i2p_node_destination
        )

        if local_i2p_node_destination is None:
            await (
                self.__close_local_i2p_node_sam_session()
            )

            return

        local_i2p_node_sam_ip_address = (
            self.__local_i2p_node_sam_ip_address
        )

        if local_i2p_node_sam_ip_address is None:
            await (
                self.__close_local_i2p_node_sam_session()
            )

            return

        local_i2p_node_sam_port = (
            self.__local_i2p_node_sam_port
        )

        if local_i2p_node_sam_port is None:
            await (
                self.__close_local_i2p_node_sam_session()
            )

            return

        print(
            'Trying to create session...'
        )

        local_i2p_node_sam_ip_address_and_port_pair = (
            str(
                local_i2p_node_sam_ip_address
            ),

            local_i2p_node_sam_port
        )

        (
            local_i2p_node_sam_session_reader,
            local_i2p_node_sam_session_writer
        ) = (
            await (
                i2plib.create_session(
                    session_name=(
                        _I2P_SAM_SESSION_NAME
                    ),

                    sam_address=(
                        local_i2p_node_sam_ip_address_and_port_pair
                    ),

                    destination=(
                        local_i2p_node_destination
                    )
                )
            )
        )

        self.__local_i2p_node_sam_session_reader = (
            local_i2p_node_sam_session_reader
        )

        self.__local_i2p_node_sam_session_writer = (
            local_i2p_node_sam_session_writer
        )

        print('Session created')


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
        application_close_event.wait()
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
