class Node(QGraphicsEllipseItem):
    def __init__(self, node_id, question, answer, x, y):
        super().__init__(0, 0, 100, 50, None)
        self.node_id = node_id
        self.question = question
        self.answer = answer
        self.setPos(x, y)
        self.setBrush(QBrush(QColor(200, 200, 255)))
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)
        
        self.text_item = QGraphicsTextItem(self)
        self.text_item.setPlainText(self.question[:10] + "...")
        self.text_item.setPos(5, 15)
        self.context_menu_methods = ["edit", "delete"]
        assert all(hasattr(self,m) for m in self.context_menu_methods), "Must implement all conext menu functions"
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.scene().parent().update_sidebar(self.question, self.answer)
        if event.button() == Qt.RightButton: self.show_context_menu(event)
        super().mousePressEvent(event)
        
    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionHasChanged:
            for line in self.scene().items():
                if isinstance(line, QGraphicsLineItem):
                    start_item = line.line().p1()
                    end_item = line.line().p2()
                    if start_item == self.pos() or end_item == self.pos():
                        new_line = QLineF(start_item, end_item)
                        line.setLine(new_line)
        return super().itemChange(change, value)
        
    def show_context_menu(self, event):
        context_menu = QMenu()
        for method_name in self.context_menu_methods:
            action = QAction(method_name.title(), context_menu)
            action.triggered.connect(getattr(self, method_name))
            context_menu.addAction(action)
        context_menu.exec_(QCursor.pos())
        
    def edit():
        pass
    def delete():
        pass