class GraphViewer(QGraphicsView):
    def __init__(self, scene, db_name, parent=None):
        super().__init__(scene, parent)
        self.db_name = db_name
        self.scene = scene
        self.node_items = {}
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, pos):
        scene_pos = self.mapToScene(pos)
        menu = QMenu()
        add_node_action = menu.addAction("Add Node")
        action = menu.exec_(self.mapToGlobal(pos))
        
        if action == add_node_action:
            self.add_new_node(scene_pos)
    
    def add_new_node(self, pos):
        question, ok = QInputDialog.getText(self, "New Flashcard", "Enter the question:")
        if ok and question:
            answer, ok = QInputDialog.getText(self, "New Flashcard", "Enter the answer:")
            if ok and answer:
                graph = FlashcardGraph(self.db_name) 
                x, y = int(pos.x()), int(pos.y())
                node_id = graph.add_node(question, answer, x, y)
                node_item = Node(node_id, question, answer, x, y)
                self.scene.addItem(node_item)
                self.node_items[node_id] = node_item
    
    def load_graph(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Load nodes
        cursor.execute('SELECT id, question, answer, x, y FROM nodes')
        nodes = cursor.fetchall()
        self.node_items = {}
        for node_id, question, answer, x, y in nodes:
            node_item = Node(node_id, question, answer, x, y)
            self.scene.addItem(node_item)
            self.node_items[node_id] = node_item
        
        # Load links
        cursor.execute('SELECT source_id, target_id FROM links')
        links = cursor.fetchall()
        for source_id, target_id in links:
            source = self.node_items[source_id]
            target = self.node_items[target_id]
            line = QGraphicsLineItem(QLineF(source.pos(), target.pos()))
            self.scene.addItem(line)
        
        conn.close()