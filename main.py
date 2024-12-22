import asyncio
import codecs

import sys
import typing

from ipaddress import (
    ip_address,
    IPv4Address,
    IPv6Address
)

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


class MainWindow(QMainWindow):
    __slots__ = (
        '__config_raw_data',
        '__local_node_address',
        '__local_node_address_line_edit',
        '__local_node_address_port',
        '__local_node_address_port_raw',
        '__local_node_address_port_line_edit',
        '__local_node_address_raw',
        '__remote_node_address_line_edit',
        '__remote_node_address_port',
        '__remote_node_address_port_raw',
        '__remote_node_address_port_line_edit',
        '__remote_node_address_raw'
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

        functionality_layout = (
            QGridLayout()
        )

        window_layout_widget = (
            QWidget()
        )

        window_layout = (
            QVBoxLayout(
                window_layout_widget
            )
        )

        local_node_address_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'IPv4/IPv6-адрес собственного узла'
                )
            )
        )

        local_node_address_line_edit = (
            QLineEdit()
        )

        local_node_address_raw: (
            typing.Optional[
                str
            ]
        ) = (
            config_raw_data.get(
                'local_node_address_raw'
            )
        )

        if local_node_address_raw:
            local_node_address_line_edit.setText(
                local_node_address_raw
            )

        local_node_address_line_edit.textChanged.connect(  # noqa
            self.__on_local_node_address_line_edit_text_changed
        )

        local_node_address_port_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'Порт собственного узла'
                )
            )
        )

        local_node_address_port_line_edit = (
            QLineEdit()
        )

        local_node_address_port_raw: (
            typing.Optional[
                str
            ]
        ) = (
            config_raw_data.get(
                'local_node_address_port_raw'
            )
        )

        if local_node_address_port_raw:
            local_node_address_port_line_edit.setText(
                local_node_address_port_raw
            )

        local_node_address_port_line_edit.textChanged.connect(  # noqa
            self.__on_local_node_address_port_line_edit_text_changed
        )

        remote_node_address_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'I2P-адрес удалённого узла'
                )
            )
        )

        remote_node_address_line_edit = (
            QLineEdit()
        )

        remote_node_address_raw: (
            typing.Optional[
                str
            ]
        ) = (
            config_raw_data.get(
                'remote_node_address_raw'
            )
        )

        if remote_node_address_raw:
            remote_node_address_line_edit.setText(
                remote_node_address_raw
            )

        remote_node_address_line_edit.textChanged.connect(  # noqa
            self.__on_remote_node_address_line_edit_text_changed
        )

        remote_node_address_port_label = (
            QtUtils.create_label(
                alignment=(
                    Qt.AlignmentFlag.AlignLeft
                ),

                label_text=(
                    'Порт удалённого узла'
                )
            )
        )

        remote_node_address_port_line_edit = (
            QLineEdit()
        )

        remote_node_address_port_raw: (
            typing.Optional[
                str
            ]
        ) = (
            config_raw_data.get(
                'remote_node_address_port_raw'
            )
        )

        if remote_node_address_port_raw:
            remote_node_address_port_line_edit.setText(
                remote_node_address_port_raw
            )

        remote_node_address_port_line_edit.textChanged.connect(  # noqa
            self.__on_remote_node_address_port_line_edit_text_changed
        )

        functionality_layout.addWidget(
            local_node_address_label,
            0, 0, 1, 1
        )

        functionality_layout.addWidget(
            local_node_address_port_label,
            0, 1, 1, 1
        )

        functionality_layout.addWidget(
            local_node_address_line_edit,
            1, 0, 1, 1
        )

        functionality_layout.addWidget(
            local_node_address_port_line_edit,
            1, 1, 1, 1
        )

        functionality_layout.addWidget(
            remote_node_address_label,
            2, 0, 1, 1
        )

        functionality_layout.addWidget(
            remote_node_address_port_label,
            2, 1, 1, 1
        )

        functionality_layout.addWidget(
            remote_node_address_line_edit,
            3, 0, 1, 1
        )

        functionality_layout.addWidget(
            remote_node_address_port_line_edit,
            3, 1, 1, 1
        )

        window_layout.addLayout(
            functionality_layout
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

        self.__local_node_address: (
            typing.Optional[
                typing.Union[
                    IPv4Address,
                    IPv6Address
                ]
            ]
        ) = None

        self.__local_node_address_line_edit = (
            local_node_address_line_edit
        )

        self.__local_node_address_port: (
            typing.Optional[
                int
            ]
        ) = None

        self.__local_node_address_port_line_edit = (
            local_node_address_port_line_edit
        )

        self.__local_node_address_port_raw: (
            typing.Optional[
                str
            ]
        ) = None

        self.__local_node_address_raw: (
            typing.Optional[
                str
            ]
        ) = None

        self.__remote_node_address_line_edit = (
            remote_node_address_line_edit
        )

        self.__remote_node_address_port: (
            typing.Optional[
                int
            ]
        ) = None

        self.__remote_node_address_port_line_edit = (
            remote_node_address_port_line_edit
        )

        self.__remote_node_address_port_raw: (
            typing.Optional[
                str
            ]
        ) = None

        self.__remote_node_address_raw: (
            typing.Optional[
                str
            ]
        ) = None

        self.__on_local_node_address_line_edit_text_changed()
        self.__on_local_node_address_port_line_edit_text_changed()

        self.__on_remote_node_address_line_edit_text_changed()
        self.__on_remote_node_address_port_line_edit_text_changed()

    def __on_local_node_address_line_edit_text_changed(
            self
    ) -> None:
        local_node_address_line_edit = (
            self.__local_node_address_line_edit
        )

        new_local_node_address_raw = (
            local_node_address_line_edit.text().strip()
        )

        old_local_node_address_raw = (
            self.__local_node_address_raw
        )

        if (
                old_local_node_address_raw is not None and
                (
                    new_local_node_address_raw ==
                    old_local_node_address_raw
                )
        ):
            return

        self.__local_node_address_raw = (
            new_local_node_address_raw
        )

        (
            self.__config_raw_data[
                'local_node_address_raw'
            ]
        ) = new_local_node_address_raw

        self.__save_config()

        new_local_node_address: (
            typing.Optional[
                typing.Union[
                    IPv4Address,
                    IPv6Address
                ]
            ]
        )

        try:
            new_local_node_address = (
                ip_address(
                    new_local_node_address_raw
                )
            )
        except ValueError:
            print(
                f'Could not parse IP address {new_local_node_address_raw!r}'
            )

            new_local_node_address = (
                None
            )

        self.__local_node_address = (
            new_local_node_address
        )

        if new_local_node_address is not None:
            local_node_address_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(0, 255, 0, 0.25);'
                ' selection-background-color: rgba(0, 255, 0, 0.5);'
                ' }'
            )
        else:
            local_node_address_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(255, 0, 0, 0.25);'
                ' selection-background-color: rgba(255, 0, 0, 0.5);'
                ' }'
            )

    def __on_local_node_address_port_line_edit_text_changed(
            self
    ) -> None:
        local_node_address_port_line_edit = (
            self.__local_node_address_port_line_edit
        )

        new_local_node_address_port_raw = (
            local_node_address_port_line_edit.text().strip()
        )

        old_local_node_address_port_raw = (
            self.__local_node_address_port_raw
        )

        if (
                old_local_node_address_port_raw is not None and

                (
                    new_local_node_address_port_raw ==
                    old_local_node_address_port_raw
                )
        ):
            return

        self.__local_node_address_port_raw = (
            new_local_node_address_port_raw
        )

        (
            self.__config_raw_data[
                'local_node_address_port_raw'
            ]
        ) = new_local_node_address_port_raw

        self.__save_config()

        new_local_node_address_port: (
            typing.Optional[
                int
            ]
        )

        if new_local_node_address_port_raw.isdigit():
            try:
                new_local_node_address_port = (
                    int(
                        new_local_node_address_port_raw
                    )
                )

                if not (
                        0 <
                        new_local_node_address_port <

                        (
                            1 <<
                            16
                        )
                ):
                    new_local_node_address_port = (
                        None
                    )
            except ValueError:
                print(
                    f'Could not parse port {new_local_node_address_port_raw!r}'
                )

                new_local_node_address_port = (
                    None
                )
        else:
            new_local_node_address_port = (
                None
            )

        self.__local_node_address_port = (
            new_local_node_address_port
        )

        if new_local_node_address_port is not None:
            local_node_address_port_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(0, 255, 0, 0.25);'
                ' selection-background-color: rgba(0, 255, 0, 0.5);'
                ' }'
            )
        else:
            local_node_address_port_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(255, 0, 0, 0.25);'
                ' selection-background-color: rgba(255, 0, 0, 0.5);'
                ' }'
            )

    def __on_remote_node_address_line_edit_text_changed(
            self
    ) -> None:
        remote_node_address_line_edit = (
            self.__remote_node_address_line_edit
        )

        new_remote_node_address_raw = (
            remote_node_address_line_edit.text().strip()
        )

        old_remote_node_address_raw = (
            self.__remote_node_address_raw
        )

        if (
                old_remote_node_address_raw is not None and
                (
                    new_remote_node_address_raw ==
                    old_remote_node_address_raw
                )
        ):
            return

        self.__remote_node_address_raw = (
            new_remote_node_address_raw
        )

        (
            self.__config_raw_data[
                'remote_node_address_raw'
            ]
        ) = new_remote_node_address_raw

        self.__save_config()

        if 1:  # TODO: check by regexp match
            remote_node_address_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(0, 255, 0, 0.25);'
                ' selection-background-color: rgba(0, 255, 0, 0.5);'
                ' }'
            )
        else:
            remote_node_address_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(255, 0, 0, 0.25);'
                ' selection-background-color: rgba(255, 0, 0, 0.5);'
                ' }'
            )

    def __on_remote_node_address_port_line_edit_text_changed(
            self
    ) -> None:
        remote_node_address_port_line_edit = (
            self.__remote_node_address_port_line_edit
        )

        new_remote_node_address_port_raw = (
            remote_node_address_port_line_edit.text().strip()
        )

        old_remote_node_address_port_raw = (
            self.__remote_node_address_port_raw
        )

        if (
                old_remote_node_address_port_raw is not None and

                (
                    new_remote_node_address_port_raw ==
                    old_remote_node_address_port_raw
                )
        ):
            return

        self.__remote_node_address_port_raw = (
            new_remote_node_address_port_raw
        )

        (
            self.__config_raw_data[
                'remote_node_address_port_raw'
            ]
        ) = new_remote_node_address_port_raw

        self.__save_config()

        new_remote_node_address_port: (
            typing.Optional[
                int
            ]
        )

        if new_remote_node_address_port_raw.isdigit():
            try:
                new_remote_node_address_port = (
                    int(
                        new_remote_node_address_port_raw
                    )
                )

                if not (
                        0 <
                        new_remote_node_address_port <

                        (
                            1 <<
                            16
                        )
                ):
                    new_remote_node_address_port = (
                        None
                    )
            except ValueError:
                print(
                    f'Could not parse port {new_remote_node_address_port_raw!r}'
                )

                new_remote_node_address_port = (
                    None
                )
        else:
            new_remote_node_address_port = (
                None
            )

        self.__remote_node_address_port = (
            new_remote_node_address_port
        )

        if new_remote_node_address_port is not None:
            remote_node_address_port_line_edit.setStyleSheet(
                'QLineEdit {'
                ' background: rgba(0, 255, 0, 0.25);'
                ' selection-background-color: rgba(0, 255, 0, 0.5);'
                ' }'
            )
        else:
            remote_node_address_port_line_edit.setStyleSheet(
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


async def main() -> None:
    app = (
        QApplication(
            sys.argv
        )
    )

    window = (
        MainWindow()
    )

    window.show()

    app.exec()


if (
        __name__ ==
        '__main__'
):
    asyncio.run(
        main()
    )
