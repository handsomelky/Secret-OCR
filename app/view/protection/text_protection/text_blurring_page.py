from PySide6.QtCore import QModelIndex, Qt, QObject, QEvent, Signal, QTimer
from PySide6.QtGui import QPalette, QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFileDialog, QFrame, QGraphicsView, QListWidgetItem

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon, ListWidget, PushButton
from qfluentwidgets import FluentIcon as FIF
from ....common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ....common.icon import Icon, FluentIconBase
from ....components.link_card import LinkCardView
from ....components.sample_card import SampleCardView
from ....common.style_sheet import StyleSheet

from ....utils.metadataTools import get_metadata, modify_metadata_and_save
from ....components.graph_scene import GraphScene,GraphicsImageItem, GraphicsPolygonItem, GraphicsMosaicItem

from ....api.paddle_ocr import perform_ocr


class VisualizationArea(QWidget):
    """ Metadata Table """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(336)

        self.hBoxLayout = QHBoxLayout(self)
        self.picArea = QFrame(self)
        self.textArea = QFrame(self)

        self.picLayout = QVBoxLayout(self.picArea)
        self.textLayout = QVBoxLayout(self.textArea)

        self.picView = QGraphicsView(self.picArea)
        self.picScene = GraphScene()

        self.textList = ListWidget(self.textArea)

        self.mosaicItems = {}
        self.isItemChangedConnected = False

        self.__initWidget()

    def __initWidget(self):
        self.initLayout()

        self.picView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.picView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.picView.setScene(self.picScene)

        self.textList.setWordWrap(True)
        self.textList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.picView.setObjectName('picView')
        self.textArea.setObjectName('textArea')

    #     self.connectSignalToSlot()
        
    # def connectSignalToSlot(self):
        
      
        
        
    def initLayout(self):

        self.picLayout.addWidget(self.picView)
        
        self.textArea.setFixedWidth(220)
        self.textLayout.addWidget(self.textList)
        self.textLayout.setContentsMargins(14, 16, 14, 14)

        self.hBoxLayout.addWidget(self.picArea, 1)
        self.hBoxLayout.addWidget(self.textArea, 0, Qt.AlignRight)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)



    def updateView(self, path, recognitions):
        """
        更新图片和识别信息
        """
        # 清空当前所有图元
        self.picScene.clear()
        self.currentRecognitions = recognitions
        # 添加图片
        self.imageItem = GraphicsImageItem(path, self.picScene)
        # 添加框
        for index, item in enumerate(recognitions):
            GraphicsPolygonItem(item["text_region"], index, self.picScene, self.textList)


    def updateText(self, recognitions):
        """
        更新listwidget文本内容
        """
        if self.isItemChangedConnected:
            self.textList.itemChanged.disconnect()
            self.isItemChangedConnected = False
        self.textList.clear()
        for recognition in recognitions:
            item = QListWidgetItem(self.textList)
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            item.setText(recognition["text"])
            item.setCheckState(Qt.CheckState.Checked)
            self.textList.indexFromItem
            self.textList.addItem(item)
        self.textList.itemChanged.connect(self.onItemChanged)
        self.isItemChangedConnected = True

    def onItemChanged(self, item):
        index = self.textList.row(item)
        if item.checkState() != Qt.CheckState.Checked:
            # 检查项的状态，如果未选中，则在对应的框图元上应用马赛克
            recognition = self.currentRecognitions[index]
            self.applyMosaicToRegion(index,recognition['text_region'])
        else:
            # 如果项被重新选中，可以移除马赛克
            if index in self.mosaicItems:
                mosaicItem = self.mosaicItems.pop(index)
                self.picScene.removeItem(mosaicItem)
            

    def applyMosaicToRegion(self, index, polygonPoints, mosaicSize=10):
        image = self.imageItem.pixmap().toImage()
        mosaicItem = GraphicsMosaicItem(image, polygonPoints, mosaicSize)
        self.picScene.addItem(mosaicItem)  # 将马赛克图元添加到场景中
        self.mosaicItems[index] = mosaicItem  # 保存索引与图元的映射





class TextBlurringPage(ScrollArea):
    """ Text Blurring """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        self.visualizationArea = VisualizationArea(self)

        self.loadFileButton = PushButton(FIF.FOLDER, 'Load File', self)

        self.saveFileButton = PushButton(FIF.SAVE, 'Save File', self)

        self.__initWidget()
    
    def __initWidget(self):
        self.initLayout()
        self.view.setObjectName('view')
        self.setObjectName('textBlurringPage')
        StyleSheet.TEXT_BLURRING_PAGE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.connectSignalToSlot()

    def connectSignalToSlot(self):

        self.loadFileButton.clicked.connect(self.load_file)
        self.saveFileButton.clicked.connect(self.save_file)

    def initLayout(self):
        
        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.loadFileButton, 0)
        self.vBoxLayout.addWidget(self.saveFileButton, 0)
        self.vBoxLayout.addWidget(self.visualizationArea, 1, Qt.AlignTop)

        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 20, 36, 36)

    def load_file(self):

        
        # 定义文件过滤器
        file_filter = "Supported Files (*.jpg *.jpeg *.pdf *.docx);;Image Files (*.jpg *.jpeg);;PDF Files (*.pdf);;Word Files (*.docx)"
        # 打开文件选择对话框，使用过滤器
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", file_filter)
        
        if file_path:
            
            self.display_visualization(file_path)

    def display_visualization(self, file_path):

        file_path_list = []
        file_path_list.append(file_path)
        self.ocr_results = perform_ocr(file_path_list)
        self.visualizationArea.updateView(file_path, self.ocr_results[0]["ocr_result"])
        self.visualizationArea.updateText(self.ocr_results[0]["ocr_result"])


    def save_file(self):

        pass