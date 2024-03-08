import random
import math
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem, QGraphicsPolygonItem, QGraphicsSceneHoverEvent, QStyle
from PySide6.QtGui import QPixmap, QPolygon, QPen, QColor, QBrush
from PySide6.QtCore import QPoint, Qt

from qfluentwidgets import ListWidget

class GraphScene(QGraphicsScene):
    """
    图像管理场景
    """
    def __init__(self):
        super().__init__()

class GraphicsPolygonItem(QGraphicsPolygonItem):
    """
    框图元
    """
    def __init__(self, points, index, parent, textList):
        super().__init__()
        # 识别结果的id
        self.index = index
        self.setAcceptHoverEvents(True)  # 启用悬停事件
        self.BOX_COLORS = [(82, 85, 255), (255, 130, 80), (240, 70, 255), (255, 255, 19), (30, 255, 30)]
        self.color = random.choices(self.BOX_COLORS)[0]
        self.points = points
        self.textList = textList
        self.setPen(QPen(QColor(*self.color), 1))
        # 画框
        self.polygon = QPolygon()
        for point in points:
            self.polygon.append(QPoint(point[0], point[1]))
        self.setPolygon(self.polygon)
        # 设置可以选择
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        parent.addItem(self)
    
    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.setBrush(QColor(*self.color, 127))
        self.setPen(QPen(QColor(*self.color), 1))
        # 取消默认的虚线
        self.state = QStyle.State_None
        self.textList.scrollToItem(self.textList.item(self.index), ListWidget.ScrollHint.PositionAtCenter)
        self.textList.setCurrentRow(self.index)
        return super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.setBrush(QColor(0, 0, 0, 0))
        self.setPen(QPen(QColor(*self.color), 1))
        return super().hoverLeaveEvent(event)


    def paint(self, painter, option, widget):
        # 设置选中样式
        if self.isSelected():
            painter.setBrush(QColor(*self.color, 127))
            painter.setPen(QPen(QColor(*self.color), 1))
            painter.drawPolygon(self.polygon)
            # 取消默认的虚线
            option.state = QStyle.State_None
            self.textList.scrollToItem(self.textList.item(self.index), ListWidget.ScrollHint.PositionAtCenter)
            self.textList.setCurrentRow(self.index)

            # self.signal.emit(self.index)
        super().paint(painter, option, widget)
    
class GraphicsImageItem(QGraphicsPixmapItem):
    """
    照片图源
    """
    def __init__(self, path, parent):
        super().__init__()
        self.pix = QPixmap(path)
        # 设置图元
        self.setPixmap(self.pix)
        # 加入图元
        parent.addItem(self)


class GraphicsMosaicItem(QGraphicsPolygonItem):
    def __init__(self, image, points, mosaicSize=10):
        """
        初始化马赛克框图元。

        :param image: 包含图像的QImage对象。
        :param points: 定义多边形顶点的点列表。
        :param mosaicSize: 马赛克的格子大小，默认为10。
        """
        super().__init__()
        self.image = image
        self.mosaicSize = mosaicSize
        self.setPen(QPen(QColor(0, 0, 0, 0)))  # 设置透明边框，不显示多边形边界

        # 创建多边形
        polygon = QPolygon()
        for point in points:
            polygon.append(QPoint(point[0], point[1]))
        self.setPolygon(polygon)

    def paint(self, painter, option, widget=None):
        # 绘制马赛克
        rect = self.polygon().boundingRect()
         # 计算需要的马赛克块数，向上取整
        mosaic_width_count = int(math.ceil(rect.width() / self.mosaicSize))
        mosaic_height_count = int(math.ceil(rect.height() / self.mosaicSize))

        # 计算调整后的马赛克覆盖范围
        adjusted_width = mosaic_width_count * self.mosaicSize
        adjusted_height = mosaic_height_count * self.mosaicSize

        # 计算额外长度和宽度，并将其均匀分布到原框的两侧
        extra_width = (adjusted_width - rect.width()) / 2
        extra_height = (adjusted_height - rect.height()) / 2

        # 调整起始点坐标
        start_x = int(math.ceil(rect.left() - extra_width))
        start_y = int(math.ceil(rect.top() - extra_height))

        # 绘制马赛克
        for i in range(mosaic_width_count):
            for j in range(mosaic_height_count):
                x = start_x + i * self.mosaicSize
                y = start_y + j * self.mosaicSize
                # 只有当多边形包含当前块的中心点时，才填充
                if self.polygon().containsPoint(QPoint(x + self.mosaicSize / 2, y + self.mosaicSize / 2), Qt.WindingFill):
                    avgColor = self.calculateAverageColor(x, y)
                    painter.fillRect(x, y, self.mosaicSize, self.mosaicSize, QBrush(avgColor))

    def calculateAverageColor(self, x, y):
        """
        计算指定区域的平均颜色。

        :param x: 区域左上角的x坐标。
        :param y: 区域左上角的y坐标。
        :return: QColor对象，表示平均颜色。
        """
        r, g, b = 0, 0, 0
        count = 0

        for i in range(x, min(x + self.mosaicSize, self.image.width())):
            for j in range(y, min(y + self.mosaicSize, self.image.height())):
                color = QColor(self.image.pixel(i, j))
                r += color.red()
                g += color.green()
                b += color.blue()
                count += 1

        return QColor(r // count, g // count, b // count) if count else QColor(0, 0, 0)
