# coding: utf-8
from typing import List
from PySide6.QtCore import Qt, Signal, QEasingCurve, QUrl, QSize
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import QApplication, QHBoxLayout, QFrame, QWidget

from qfluentwidgets import (NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow,
                            SplashScreen, ScrollArea)
from qfluentwidgets import FluentIcon as FIF

from .home_page import HomePage
from .protection.protection_page import ProtectionPage
from .protection.text_protection.text_protection_page import TextProtectionPage
from .protection.text_protection.metadata_clean_page import MetadataCleanPage
from .protection.text_protection.text_blurring_page import TextBlurringPage
from .protection.face_protection.face_protection_page import FaceProtectionPage
from .secret.secret_page import SecretPage
from .setting_interface import SettingInterface
from ..common.config import ZH_SUPPORT_URL, EN_SUPPORT_URL, cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common.translator import Translator
from ..common import resource


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # create sub interface
        self.homeInterface = HomePage(self)
        self.protectionPage = ProtectionPage(self)
        self.textProtectionPage = TextProtectionPage(self)
        self.metadataCleanPage = MetadataCleanPage(self)
        self.textBlurringPage = TextBlurringPage(self)
        self.faceProtectionPage = FaceProtectionPage(self)
        self.secretPage = SecretPage(self)

        self.settingInterface = SettingInterface(self)


        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToSampleCard.connect(self.switchToSample)
        signalBus.supportSignal.connect(self.onSupport)

    def initNavigation(self):
        # add navigation items
        t = Translator()
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        self.addSubInterface(self.protectionPage, FIF.FINGERPRINT, t.protection)
        self.addSubInterface(self.textProtectionPage, Icon.TEXT, t.textProtection, parent=self.protectionPage)
        self.addSubInterface(self.metadataCleanPage, Icon.METADATA_CLEAN, t.metadataClean, parent=self.textProtectionPage)
        self.addSubInterface(self.textBlurringPage, Icon.MOSAIC, t.textBlurring, parent=self.textProtectionPage)
        self.addSubInterface(self.faceProtectionPage, Icon.FACE, t.faceProtection, parent=self.protectionPage)
        self.addSubInterface(self.secretPage, Icon.DATASHARING, 'Secret')
        self.navigationInterface.addSeparator()

        pos = NavigationItemPosition.SCROLL

        # add custom widget to bottom
        self.navigationInterface.addItem(
            routeKey='price',
            icon=Icon.PRICE,
            text=t.price,
            onClick=self.onSupport,
            selectable=False,
            tooltip=t.price,
            position=NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle('PyQt-Fluent-Widgets')

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def onSupport(self):
        language = cfg.get(cfg.language).value
        if language.name() == "zh_CN":
            QDesktopServices.openUrl(QUrl(ZH_SUPPORT_URL))
        else:
            QDesktopServices.openUrl(QUrl(EN_SUPPORT_URL))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def switchToSample(self, routeKey):
        """ switch to sample """
        interfaces = self.findChildren(ScrollArea)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackedWidget.setCurrentWidget(w, False)
