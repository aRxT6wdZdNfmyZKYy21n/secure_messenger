from base64 import (
    b64encode
)

from PyQt6.QtCore import (
# from PySide6.QtCore import (
    QBuffer,
    Qt
)

from PyQt6.QtGui import (
# from PySide6.QtGui import (
    QImage
)

from PyQt6.QtWidgets import (
# from PySide6.QtWidgets import (
    # QComboBox,
    QLabel
)


class QtUtils(object):
    @staticmethod
    def create_label(
            label_text: str,

            alignment=(
                Qt.AlignmentFlag.AlignCenter
            )
    ) -> QLabel:
        label = (
            QLabel(
                label_text
            )
        )

        label.setAlignment(
            alignment
        )

        label.adjustSize()

        return (
            label
        )


    @staticmethod
    def get_image_base64_encoded_text(
            image: (
                QImage
            )
    ) -> str:
        image_buffer = (
            QBuffer()
        )

        image.save(
            image_buffer,

            format=(
                'png'
            )
        )

        return (
            b64encode(
                image_buffer.data()
            ).decode()
        )

    @classmethod
    def get_image_html_text(
            cls,

            image_base64_encoded_text: (
                str
            )
    ) -> str:
        return (
            '<img'
            f' src="data:image/png;base64, {image_base64_encoded_text}"'
            ' />'
        )