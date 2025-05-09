import asyncio
import logging
import os
import sys

import i2plib  # noqa

from PyQt6.QtWidgets import (
# from PySide6.QtWidgets import (
    QApplication
)

from qasync import (
    QEventLoop
)

from gui.main_window import (
    MainWindow
)

from helpers.custom_stream_handler import (
    CustomStreamHandler
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
