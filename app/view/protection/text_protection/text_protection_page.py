# coding:utf-8
import json

from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon
from ....common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ....components.sample_card import SampleCardView
from ....common.style_sheet import StyleSheet



class TextProtectionPage(ScrollArea):
    """ Text Protection """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()
        self.loadSamples()

    def __initWidget(self):
        self.view.setObjectName('view')
        self.setObjectName('textProtectionPage')
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def loadSamples(self):
        """ load samples """
        # Text Protection samples
        TextProtectionView = SampleCardView(
            self.tr("Text Protection"), self.view)
        TextProtectionView.addSampleCard(
            icon=":/gallery/images/controls/Button.png",
            title="Metadata Clean",
            content=self.tr(
                "Remove potentially privacy-exposing metadata from files securely."),
            routeKey="metadataCleanPage",
        )
        TextProtectionView.addSampleCard(
            icon=":/gallery/images/controls/Button.png",
            title="Text Blurring",
            content=self.tr(
                "Recognizes and blurs sensitive text in images to protect privacy."),
            routeKey="textBlurringPage",
        )
        self.vBoxLayout.addWidget(TextProtectionView)