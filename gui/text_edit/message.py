import logging
import typing

import i2plib  # noqa

from PyQt6.QtCore import (
# from PySide6.QtCore import (
    QMimeData,
    Qt
)

from PyQt6.QtGui import (
    QImage,
    QKeyEvent, QKeySequence
)

from PyQt6.QtWidgets import (
# from PySide6.QtWidgets import (
    QTextEdit
)

from events.async_event import (
    AsyncEvent
)

from utils.qt import (
    QtUtils
)


logger = (
    logging.getLogger(
        __name__
    )
)


class MessageTextEdit(QTextEdit):
    __slots__ = (
        '__images',
        '__on_message_send_key_pressed_event'
    )

    def __init__(
            self
    ) -> None:
        super(
            MessageTextEdit,
            self
        ).__init__()

        self.document().contentsChanged.connect(  # noqa
            self.__update_height
        )

        self.__images: (
            typing.List[
                QImage
            ]
        ) = []

        self.__on_message_send_key_pressed_event = (
            AsyncEvent(
                'OnMessageSendKeyPressedEvent'
            )
        )

        self.__update_height()

    def clear(self) -> None:
        super(
            MessageTextEdit,
            self
        ).clear()

        self.__images.clear()

    def get_on_message_send_key_pressed_event(
            self
    ) -> AsyncEvent:
        return (
            self.__on_message_send_key_pressed_event
        )

    def images(
            self
    ) -> (
            typing.List[
                QImage
            ]
    ):
        return (
            self.__images
        )

    def insertFromMimeData(
            self,

            source: (
                QMimeData
            )
    ) -> None:
        if (
                source.hasImage()
        ):
            image: (
                QImage
            ) = source.imageData()

            self.__add_image(
                image
            )
        elif (
                source.hasUrls()
        ):
            urls = (
                source.urls()
            )

            for url in (
                    urls
            ):
                if not url.isLocalFile():
                    logger.warning(
                        'Non-local file URL is not supported'
                        f': {url}'
                    )

                    continue

                image = (
                    QImage()
                )

                if not (
                        image.load(
                            url.path()
                        )
                ):
                    logger.warning(
                        'Could not load image by URL'
                        f': {url}'
                    )

                    continue

                self.__add_image(
                    image
                )
        elif (
                source.hasHtml()
        ):
            html_text = (
                source.html()
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

                for image in (
                        images
                ):
                    self.__add_image(
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

                self.insertPlainText(
                    plain_text
                )

        elif (
                source.hasText()
        ):
            self.insertPlainText(
                source.text()
            )
        else:
            print(
                'hasColor'
                f': {source.hasColor()!r}'
            )

            print(
                'colorData'
                f': {source.colorData()!r}'
            )

            print(
                'hasHtml'
                f': {source.hasHtml()!r}'
            )

            print(
                'html'
                f': {source.html()!r}'
            )

            print(
                'hasImage'
                f': {source.hasImage()!r}'
            )

            print(
                'imageData'
                f': {source.imageData()!r}'
            )

            print(
                'hasText'
                f': {source.hasText()!r}'
            )

            print(
                'text'
                f': {source.text()!r}'
            )

            print(
                'hasUrls'
                f': {source.hasUrls()!r}'
            )

            print(
                'urls'
                f': {source.urls()!r}'
            )

    def keyPressEvent(
            self,

            event: (
                QKeyEvent
            )
    ) -> None:
        key = (
            event.key()
        )

        if (
                key not in

                (
                    Qt.Key.Key_Enter,
                    Qt.Key.Key_Return
                )
        ):
            super(
                MessageTextEdit,
                self
            ).keyPressEvent(
                event
            )

            return

        modifier = (
            event.modifiers()
        )

        if (
                modifier not in

                (
                    Qt.KeyboardModifier.NoModifier,
                    Qt.KeyboardModifier.KeypadModifier
                )
        ):
            super(
                MessageTextEdit,
                self
            ).keyPressEvent(
                event
            )

            return

        print(
            'on_message_send_key_pressed_event'
        )

        self.__on_message_send_key_pressed_event()

    def __add_image(
            self,

            image: (
                QImage
            )
    ) -> None:
        self.__images.append(
            image
        )

        self.insertHtml(
            QtUtils.get_image_html_text(
                QtUtils.get_image_base64_encoded_text(
                    image
                )
            )
        )

        self.insertPlainText(
            '\n'
        )

    def __update_height(
            self
    ) -> None:
        new_minimum_height = (
            min(
                max(
                    int(
                        self.document().size().height()
                    ),

                    25
                ),

                500
            )
        )

        old_minimum_height = (
            self.minimumHeight()
        )

        if (
                new_minimum_height ==
                old_minimum_height
        ):
            return

        print(
            'new_minimum_height'
            f': {new_minimum_height}'
        )

        self.setMinimumHeight(
            new_minimum_height
        )
