class FlashcardGraphGUI(QMainWindow):
    def __init__(self, db_name):
        super().__init__()
        self.db_name = db_name
        self.initUI()
        
    def initUI(self):
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle('Flashcard Graph')
        
        # Create a central widget and a splitter
        central_widget = QWidget()
        splitter = QSplitter(Qt.Horizontal)
        
        # Create the scene and the graph view
        self.scene = QGraphicsScene(self)
        self.graph_view = GraphView(self.scene, self.db_name, self)
        splitter.addWidget(self.graph_view)
        
        # Create the sidebar
        self.sidebar = Sidebar(self)
        splitter.addWidget(self.sidebar)
        
        # Set splitter sizes
        splitter.setSizes([700, 300])
        
        # Create layout and add splitter
        layout = QVBoxLayout(central_widget)
        layout.addWidget(splitter)
        
        # Create the Save button
        save_button = QPushButton("Save Positions")
        save_button.clicked.connect(self.save_positions)
        layout.addWidget(save_button)
        
        # Set the central widget
        self.setCentralWidget(central_widget)
        
        # Load the graph
        self.graph_view.load_graph()
        
    def update_sidebar(self, question, answer):
        self.sidebar.update_content(question, answer)
        
    def save_positions(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            for node_id, node_item in self.graph_view.node_items.items():
                x = int(node_item.pos().x())
                y = int(node_item.pos().y())
                cursor.execute('UPDATE nodes SET x = ?, y = ? WHERE id = ?', (x, y, node_id))
            
            conn.commit()
            QMessageBox.information(self, "Success", "Positions saved successfully!")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
        finally:
            conn.close()
            
    def closeEvent(self, event):
        self.save_positions()
        super().closeEvent(event)

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.top_sidebar = AnkiSidebar(self)
        self.bottom_sidebar = GraphMenuSidebar(self)
        
        # Set up vertical splitter
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.top_sidebar)
        splitter.addWidget(self.bottom_sidebar)
        splitter.setSizes([150, 100])
        # Set layout
        layout = QVBoxLayout(self)
        layout.addWidget(splitter)
        self.setLayout(layout)
        
    def update_content(self, question, answer): self.top_sidebar.update_content(question, answer)
    def display_settings(self): self.bottom_sidebar.display_settings()