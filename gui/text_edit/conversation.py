import logging
import typing

import i2plib  # noqa

from PyQt6.QtCore import (
    QMimeData
)

from PyQt6.QtGui import (
    QImage
)

from PyQt6.QtWidgets import (
    QTextEdit
)

from utils.qt import (
    QtUtils
)


logger = (
    logging.getLogger(
        __name__
    )
)


class ConversationTextEdit(QTextEdit):
    def createMimeDataFromSelection(
            self
    ) -> (
            QMimeData
    ):
        mime_data = (
            QMimeData()
        )

        text_cursor = (
            self.textCursor()
        )

        if not (
                text_cursor.hasSelection()
        ):
            return (
                mime_data
            )

        html_text = (
            text_cursor.selection().toHtml()
        )

        result_raw_data = (
            QtUtils.parse_html(
                html_text
            )
        )

        images: (
            typing.Optional[
                typing.List[
                    QImage
                ]
            ]
        ) = (
            result_raw_data[
                'images'
            ]
        )

        if images is not None:
            print(
                'found images count'
                f': {len(images)}'
            )

            if (
                    len(
                        images
                    ) !=

                    1
            ):
                logger.warning(
                    'Could not set more than one image into QMimeData'
                )

            image = (
                images[
                    0
                ]
            )

            mime_data.setImageData(
                image
            )

        plain_text: str = (
            result_raw_data[
                'plain_text'
            ]
        )

        if plain_text:
            print(
                'plain text'
                f': {plain_text!r}'
            )

            mime_data.setText(
                plain_text
            )

        return (
            mime_data
        )
