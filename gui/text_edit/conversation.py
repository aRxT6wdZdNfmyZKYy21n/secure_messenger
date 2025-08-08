import logging

from PySide6.QtCore import (
    QMimeData,
)

from PySide6.QtGui import (
    QImage,
)

from PySide6.QtWidgets import (
    QTextEdit,
)

from utils.qt import (
    QtUtils,
)


logger = logging.getLogger(
    __name__,
)


class ConversationTextEdit(QTextEdit):
    def createMimeDataFromSelection(self) -> QMimeData:
        mime_data = QMimeData()

        text_cursor = self.textCursor()

        if not (text_cursor.hasSelection()):
            return mime_data

        html_text = text_cursor.selection().toHtml()

        result_raw_data = QtUtils.parse_html(
            html_text,
        )

        images: list[QImage] | None = result_raw_data['images']

        if images is not None:
            logger.debug(
                'found images count: %s',
                len(images),
            )

            if len(images) != 1:
                logger.warning(
                    'Could not set more than one image into QMimeData',
                )

            image = images[0]

            mime_data.setImageData(
                image,
            )

        plain_text: str = result_raw_data['plain_text']

        if plain_text:
            logger.debug(
                'plain text: %r',
                plain_text,
            )

            mime_data.setText(
                plain_text,
            )

        return mime_data
