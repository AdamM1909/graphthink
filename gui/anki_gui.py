class AnkiSidebar(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
    
    def update_content(self, question, answer):
        self.clear()
        self.append("<h3>Question:</h3>")
        self.append(question)
        self.append("<h3>Answer:</h3>")
        self.append(answer)