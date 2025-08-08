import logging
import io
import typing

from base64 import (
    b64decode,
    b64encode
)

from lxml import (
    etree
)

from PySide6.QtCore import (
    QBuffer,
    Qt
)

from PySide6.QtGui import (
    QImage
)

from PySide6.QtWidgets import (
    # QComboBox,
    QLabel
)


_HTML_IMAGE_SOURCE_PNG_BASE_64_PREFIX = (
    'data:image/png;base64,'
)


logger = (
    logging.getLogger(
        __name__,
    )
)


class QtUtils(object):
    @staticmethod
    def create_label(
            label_text: str,

            alignment=(
                Qt.AlignmentFlag.AlignCenter
            ),
    ) -> QLabel:
        label = (
            QLabel(
                label_text,
            )
        )

        label.setAlignment(
            alignment,
        )

        label.adjustSize()

        return (
            label
        )


    @staticmethod
    def get_image_base64_encoded_text(
            image: (
                QImage
            ),
    ) -> str:
        image_buffer = (
            QBuffer()
        )

        image.save(
            image_buffer,

            format=(
                b'png'
            ),
        )

        return (
            b64encode(
                image_buffer.data().data(),
            ).decode()
        )

    @classmethod
    def get_image_html_text(
            cls,

            image_base64_encoded_text: (
                str
            ),
    ) -> str:
        return (
            '<img'
            f' src="{_HTML_IMAGE_SOURCE_PNG_BASE_64_PREFIX} {image_base64_encoded_text}"'
            ' />'
        )

    @staticmethod
    def parse_html(
            html_text: (
                str
            ),
    ) -> dict[str, typing.Any]:
        parser = (
            etree.HTMLParser(
                remove_comments=(
                    True
                ),
            )
        )

        root: (
            etree._Element  # noqa
        ) = (
            etree.fromstring(
                html_text,
                parser,
            )
        )

        body_elements: (
            list[
                etree._Element  # noqa
            ]
        ) = (
            list(
                root.iterchildren(
                    tag='body',
                )
            )
        )

        assert (
            len(
                body_elements,
            ) ==

            1
        )

        body_element = (
            body_elements[
                0
            ]
        )

        plain_text_io = (
            io.StringIO()
        )

        images: (
            list[
                QImage
            ] | None
        ) = None

        element: (
            etree._Element  # noqa
        )

        for element in (
                body_element.iter()
        ):
            if (
                    element.tag ==
                    'img'
            ):
                image_source: str = (
                    element.attrib.get(
                        'src',
                    )
                )

                if not image_source:
                    continue

                if (
                        image_source.startswith(
                            _HTML_IMAGE_SOURCE_PNG_BASE_64_PREFIX,
                        )
                ):
                    image_base64_encoded_text = (
                        image_source.removeprefix(
                            _HTML_IMAGE_SOURCE_PNG_BASE_64_PREFIX,
                        ).lstrip()
                    )

                    if not image_base64_encoded_text:
                        continue

                    image = (
                        QImage()
                    )

                    if not (
                            image.loadFromData(
                                b64decode(
                                    image_base64_encoded_text,
                                ),

                                format=(
                                    b'png'
                                ),
                            )
                    ):
                        logger.warning(
                            'Could not load image'
                            f' with Base64-encoded text {image_base64_encoded_text!r}',
                        )

                        continue

                    if images is None:
                        images = []

                    images.append(
                        image,
                    )
                else:
                    logger.warning(
                        'Image'
                        f' with source {image_source!r}'
                        ' is not supported',
                    )

                continue

            element_text = (
                element.text
            )

            if element_text:
                plain_text_io.write(
                    element_text,
                )

        plain_text_io.seek(
            0,
        )

        plain_text = (
            plain_text_io.read()
        )

        return {
            'images': (
                images
            ),

            'plain_text': (
                plain_text
            ),
        }