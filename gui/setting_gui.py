class GraphMenuSidebar(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
    
    def display_settings(self):
        self.clear()
        self.append("<h3>Settings</h3>")