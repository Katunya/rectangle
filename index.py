import sys
import random
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsLineItem, QGraphicsItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QPainter


class GraphicsView(QGraphicsView):
    def __init__(self):
        super(GraphicsView, self).__init__()
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setSceneRect(0, 0, 800, 600)
        self.rectangles = []
        self.lines = []
        self.double_click_pos = None

    def mouseDoubleClickEvent(self, event):
        self.double_click_pos = event.pos()
        if self.sceneRect().contains(self.mapToScene(event.pos())):
            rect = RectangleItem(random_color())
            if check_space_for_rectangle(rect):
                rect.setPos(self.mapToScene(event.pos()) - QPointF(RECT_WIDTH / 2, RECT_HEIGHT / 2))
                self.scene().addItem(rect)
                self.rectangles.append(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.item_to_move = self.itemAt(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.item_to_move:
            for line in self.lines:
                line.update_position()
            self.item_to_move = None

    def mouseMoveEvent(self, event):
        if self.item_to_move:
            self.item_to_move.setPos(self.mapToScene(event.pos()))
            self.adjust_collisions(self.item_to_move)

    def adjust_collisions(self, moved_item):
        colliding_items = moved_item.collidingItems(Qt.IntersectsItemBoundingRect)
        for item in colliding_items:
            if isinstance(item, RectangleItem) and item != moved_item:
                old_pos = moved_item.scenePos()
                new_pos = old_pos - moved_item.pos() + moved_item.mapToItem(item, 0, 0)
                moved_item.setPos(new_pos)
                self.adjust_collisions(moved_item)

    def drawLineBetweenRectangles(self, start_item, end_item):
        line = LineItem(start_item, end_item)
        self.scene().addItem(line)
        self.lines.append(line)
        line.update_position()


RECT_WIDTH = 100
RECT_HEIGHT = 50

class RectangleItem(QGraphicsRectItem):
    def __init__(self, color, parent=None):
        super(RectangleItem, self).__init__(parent)
        self.setRect(0, 0, RECT_WIDTH, RECT_HEIGHT)
        self.setBrush(QColor(color))
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            #  for collisions
            colliding_items = self.collidingItems(Qt.IntersectsItemBoundingRect)
            for item in colliding_items:
                if isinstance(item, RectangleItem):
                    return QPointF(0, 0)
        return super(RectangleItem, self).itemChange(change, value)


class LineItem(QGraphicsLineItem):
    def __init__(self, start_item, end_item, parent=None):
        super(LineItem, self).__init__(parent)
        self.start_item = start_item
        self.end_item = end_item
        self.update_position()

    def update_position(self):
        start_point = self.start_item.rect().center()
        end_point = self.end_item.rect().center()
        self.setLine(start_point.x(), start_point.y(), end_point.x(), end_point.y())


def check_space_for_rectangle(rect_item):
    colliding_items = rect_item.collidingItems(Qt.IntersectsItemBoundingRect)
    for item in colliding_items:
        if isinstance(item, RectangleItem):
            return False
    return True

def random_color():
    return QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = GraphicsView()
    view.show()
    sys.exit(app.exec_())
