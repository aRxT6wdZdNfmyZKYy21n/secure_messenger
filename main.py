import asyncio
import logging
import os
import sys

import i2plib  # noqa

from PyQt6.QtGui import (
    QFontDatabase
)

from PyQt6.QtWidgets import (
    QApplication
)

from qasync import (
    QEventLoop
)

from common import (
    Constants
)

from globals.common import (
    g_common_globals
)

from gui.main_window import (
    MainWindow
)

from helpers.custom_stream_handler import (
    CustomStreamHandler
)

from utils.os import (
    OsUtils
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


async def run_application(
        application: (
            QApplication
        )
) -> None:
    # Set up application fonts

    # TODO:
    #   render glyph failed err=9e
    #   QFontEngine: Glyph rendered in unknown pixel_mode=0

    assert (
        QFontDatabase.addApplicationFont(
            OsUtils.get_path(
                './'
                'data/'
                'static/'
                # 'NotoColorEmoji-Regular.ttf'
                'NotoColorEmoji.ttf'
                # 'Noto-COLRv1.ttf'
            )
        ) ==

        0
    ), (
        'Could not load emoji font'
    )

    QFontDatabase.addApplicationEmojiFontFamily(
        # 'NotoColorEmoji-Regular'
        'Noto Color Emoji'
    )

    # Set up events

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
    # Create data directory

    data_directory_path = (
        Constants.Path.DataDirectory
    )

    if not (
            os.path.exists(
                data_directory_path
            )
    ):
        os.makedirs(
            data_directory_path
        )

    # Set up logging

    logging_handlers = [
        CustomStreamHandler()
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

    g_common_globals.init_asyncio_event_loop(
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
