import typing

from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import (
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

        return label
