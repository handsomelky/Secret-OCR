from PySide6.QtCore import QMetaMethod, QModelIndex, Qt, QObject, QEvent, Signal, QTimer
from PySide6.QtGui import QPalette, QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QFileDialog, QTableWidgetItem, QHeaderView, QCompleter

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon, TableWidget, CheckBox, SearchLineEdit, PushButton, TransparentToolButton, TransparentToggleToolButton, CommandBar
from qfluentwidgets import FluentIcon as FIF
from ....common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ....common.icon import Icon, FluentIconBase
from ....components.link_card import LinkCardView
from ....components.sample_card import SampleCardView
from ....common.style_sheet import StyleSheet

from ....utils.metadataTools import get_metadata, modify_metadata_and_save


class SearchBox(SearchLineEdit):
    """ Search Box """
    return_pressed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            if self.text()!='':#非空才触发信号，为空的时候触发了没意义。
                self.return_pressed.emit(self.text())
        super().keyPressEvent(event)

class MetadataTable(QWidget):
    """ Metadata Table """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(336)

        self.hBoxLayout = QHBoxLayout(self)
        self.tableArea = QFrame(self)
        self.controlPanel = QFrame(self)

        self.tableLayout = QVBoxLayout(self.tableArea)
        self.panelLayout = QVBoxLayout(self.controlPanel)

        self.searchBar = CommandBar(self.tableArea)
        self.searchBox = SearchBox(self.searchBar)
        self.upButton = TransparentToolButton(FIF.UP, self.searchBar)
        self.downButton = TransparentToolButton(FIF.DOWN, self.searchBar)
        self.filterButton = TransparentToggleToolButton(FIF.FILTER, self.searchBar)
        self.table = TableWidget(self.tableArea)

        self.loadFileButton = PushButton(FIF.FOLDER, 'Load File', self.controlPanel)

        self.saveFileButton = PushButton(FIF.SAVE, 'Save File', self.controlPanel)

        self.currentResultIndex = 0
        self.isFiltered = False
        self.searchResults = []

        self.__initWidget()

    def __initWidget(self):
        self.initLayout()

        self.searchBox.setClearButtonEnabled(True)
        self.searchBox.setPlaceholderText('Search Metadata')

        self.upButton.setToolTip("Previous Result")
        self.downButton.setToolTip("Next Result")
        self.filterButton.setToolTip("Show Search Result Only")
        self.updateButtonsState()

        self.searchBar.addWidget(self.searchBox)
        self.searchBar.addWidget(self.upButton)
        self.searchBar.addWidget(self.downButton)
        self.searchBar.addWidget(self.filterButton)
        

        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Metadata', 'Value'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().hide()

        self.table.setObjectName('table')
        self.controlPanel.setObjectName('controlPanel')

        self.connectSignalToSlot()
        
    def connectSignalToSlot(self):
        
        self.searchBox.searchSignal.connect(self.search)
        self.searchBox.return_pressed.connect(self.search)
        self.searchBox.clearSignal.connect(self.searchClear)
        self.upButton.clicked.connect(self.gotoPreviousResult)
        self.downButton.clicked.connect(self.gotoNextResult)
        self.filterButton.toggled.connect(self.toggleFilter)
        self.loadFileButton.clicked.connect(self.load_file)
        self.saveFileButton.clicked.connect(self.save_file)
        
        
    def initLayout(self):

        self.searchBox.setFixedWidth(200)
        self.upButton.setFixedWidth(24)
        self.downButton.setFixedWidth(24)
        self.filterButton.setFixedWidth(24)

        self.controlPanel.setFixedWidth(220)

        self.tableLayout.addWidget(self.searchBar)
        self.tableLayout.addWidget(self.table)

        self.hBoxLayout.addWidget(self.tableArea, 1)
        self.hBoxLayout.addWidget(self.controlPanel, 0, Qt.AlignRight)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        self.panelLayout.setSpacing(8)
        self.panelLayout.setContentsMargins(14, 16, 14, 14)
        self.panelLayout.addWidget(self.loadFileButton)

        self.panelLayout.addSpacing(5)
        self.panelLayout.addWidget(self.saveFileButton)

        self.panelLayout.setAlignment(Qt.AlignTop)


    def load_file(self):
        # 定义文件过滤器
        file_filter = "Supported Files (*.jpg *.jpeg *.pdf *.docx);;Image Files (*.jpg *.jpeg);;PDF Files (*.pdf);;Word Files (*.docx)"
        # 打开文件选择对话框，使用过滤器
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", file_filter)
        if file_path:
            # 读取并显示元数据
            self.file_path = file_path
            self.searchClear()
            self.display_metadata(file_path)

    def display_metadata(self, file_path):

        prompts = []
        
        metadata = get_metadata(file_path)
        # 在表格中显示元数据
        self.table.setRowCount(len(metadata))
        for i, (key, value) in enumerate(metadata.items()):
            prompts.append(str(key))
            metadata_key = QTableWidgetItem(str(key))
            metadata_key.setFlags(~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, metadata_key)
            self.table.setItem(i, 1, QTableWidgetItem(str(value)))
        completer = QCompleter(prompts, self.searchBox)

        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setMaxVisibleItems(10)
        self.searchBox.setCompleter(completer)

    def search(self, searchText):
        self.searchText = searchText
        self.searchResults = self.table.findItems(searchText, Qt.MatchFlag.MatchContains)
        self.searchResults = [item for item in self.searchResults if item.column() == 0]  # 仅保留第一列的结果
        if self.isFiltered:
            self.applyFilter()
        self.scrollToResult(self.currentResultIndex)
        self.updateButtonsState()

    def scrollToResult(self, index):
        if 0 <= index < len(self.searchResults):
            self.table.selectRow(self.searchResults[index].row())
            self.table.scrollToItem(self.searchResults[index], TableWidget.ScrollHint.PositionAtCenter)

    def gotoPreviousResult(self):
        if self.searchResults:
            self.currentResultIndex = (self.currentResultIndex - 1) % len(self.searchResults)
            self.scrollToResult(self.currentResultIndex)

    def gotoNextResult(self):
        if self.searchResults:
            self.currentResultIndex = (self.currentResultIndex + 1) % len(self.searchResults)
            self.scrollToResult(self.currentResultIndex)

    def updateButtonsState(self):
        # 检查是否有搜索结果
        hasResults = bool(self.searchResults)
        self.upButton.setEnabled(hasResults)
        self.downButton.setEnabled(hasResults)
        self.filterButton.setEnabled(hasResults)

    def applyFilter(self):
        """根据搜索文本过滤表格显示"""
        self.table.setUpdatesEnabled(False)  # 暂时停止表格的更新以提高性能
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0) 
            if self.searchText.lower() in item.text().lower():
                self.table.setRowHidden(row, False)  # 如果文本匹配，则显示行
            else:
                self.table.setRowHidden(row, True)  # 如果文本不匹配，则隐藏行
        self.table.setUpdatesEnabled(True)  # 重新启用表格更新

    def resetFilter(self):
        """重置过滤，使所有行都可见"""
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, False)
        

    def toggleFilter(self):
        """切换过滤状态"""
        if self.isFiltered:
            self.resetFilter()  # 如果当前已经过滤，点击按钮则重置过滤
            QTimer.singleShot(50, lambda: self.scrollToResult(self.currentResultIndex))
        else:
            self.applyFilter()  # 如果当前未过滤，点击按钮则应用过滤
        self.isFiltered = not self.isFiltered  # 切换过滤状态标志

    def searchClear(self):
        if self.isFiltered:
            self.resetFilter()
            self.filterButton.toggle()
        self.table.clearSelection()
        self.searchText = ""
        self.searchResults = []
        self.currentResultIndex = 0
        self.updateButtonsState()

    def getCurrentMetadata(self):
        """ 遍历表格中的每一行，收集元数据键值对 """
        metadata = {}
        for row in range(self.table.rowCount()):
            key_item = self.table.item(row, 0)  # 第一列是键
            value_item = self.table.item(row, 1)  # 第二列是值
            if key_item and value_item:  # 确保项不是None
                key = key_item.text()
                value = value_item.text()
                metadata[key] = value
        return metadata
    
    def save_file(self):
        
        current_metadata = self.getCurrentMetadata()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*)")

        modify_metadata_and_save(self.file_path, current_metadata, save_path)


        


class MetadataCleanPage(ScrollArea):
    """ Metadata Clean """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()
    
    def __initWidget(self):
        self.initLayout()
        self.view.setObjectName('view')
        self.setObjectName('metadataCleanPage')
        StyleSheet.META_DATA_CLEAN_PAGE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        
        
        self.connectSignalToSlot()

    def connectSignalToSlot(self):

        pass

    def initLayout(self):

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(MetadataTable(self), 1, Qt.AlignTop)

        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 20, 36, 36)