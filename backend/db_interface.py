import sqlite3

class GraphDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def add_node(self, question, answer, x, y, node_types=[]):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO nodes (question, answer, x, y) VALUES (?, ?, ?, ?)", (question, answer, x, y))
        node_id = cursor.lastrowid
        for node_type in node_types: cursor.execute("INSERT INTO node_type_associations (node_id, type_id) VALUES (?, ?)", (node_id, self._get_node_type_id(node_type)))
        self.conn.commit()
        return node_id
    
    def add_edge(self, source_id, target_id, edge_types=[]):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO edges (source_id, target_id) VALUES (?, ?)", (source_id, target_id))
        edge_id = cursor.lastrowid
        for edge_type in edge_types: cursor.execute("INSERT INTO edge_type_associations (edge_id, type_id) VALUES (?, ?)", (edge_id, self._get_edge_type_id(edge_type)))
        self.conn.commit()
        return edge_id
    
    def get_nodes_connected_by_edge_type(self, edge_type_name):
            edge_type_id = self._get_edge_type_id(edge_type_name)
            
            query = """
            SELECT DISTINCT n.id AS node_id, n.question, n.answer, n.x, n.y,
                            GROUP_CONCAT(DISTINCT nt.name) AS node_types
            FROM nodes n
            JOIN edges e ON n.id = e.source_id OR n.id = e.target_id
            JOIN edge_type_associations eta ON e.id = eta.edge_id
            LEFT JOIN node_type_associations nta ON n.id = nta.node_id
            LEFT JOIN node_types nt ON nta.type_id = nt.id
            WHERE eta.type_id = ?
            GROUP BY n.id
            """
            
            cursor = self.conn.cursor()
            cursor.execute(query, (edge_type_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_node_types(self, node_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT nt.name FROM node_type_associations nta JOIN node_types nt ON nta.type_id = nt.id WHERE nta.node_id = ?", (node_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def get_edge_types(self, edge_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT et.name FROM edge_type_associations eta JOIN edge_types et ON eta.type_id = et.id WHERE eta.edge_id = ?", (edge_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def close(self):
        self.conn.close()

    def _get_node_type_id(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM node_types WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result[0] if result else self._add_node_type(name)
    
    def _add_node_type(self, name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO node_types (name) VALUES (?)", (name,))
        self.conn.commit()
        return cursor.lastrowid

    def _get_edge_type_id(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM edge_types WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result[0] if result else self._add_edge_type(name)
    
    def _add_edge_type(self, name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO edge_types (name) VALUES (?)", (name,))
        self.conn.commit()
        return cursor.lastrowid
    
    def _create_tables(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, question TEXT, answer TEXT, x INTEGER, y INTEGER)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS node_types (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS edges (id INTEGER PRIMARY KEY, source_id INTEGER, target_id INTEGER, FOREIGN KEY (source_id) REFERENCES nodes (id), FOREIGN KEY (target_id) REFERENCES nodes (id))")
        self.conn.execute("CREATE TABLE IF NOT EXISTS edge_types (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS node_type_associations (node_id INTEGER, type_id INTEGER, FOREIGN KEY (node_id) REFERENCES nodes (id), FOREIGN KEY (type_id) REFERENCES node_types (id), PRIMARY KEY (node_id, type_id))")
        self.conn.execute("CREATE TABLE IF NOT EXISTS edge_type_associations (edge_id INTEGER, type_id INTEGER, FOREIGN KEY (edge_id) REFERENCES edges (id), FOREIGN KEY (type_id) REFERENCES edge_types (id), PRIMARY KEY (edge_id, type_id))")
        self.conn.commit()
        
if __name__ == '__main__':
    # Create an instance of GraphDB
    db = GraphDB('black_holes.sqlite')

    # Add nodes (flashcards) about black holes
    node1_id = db.add_node(question="What is a black hole?", answer="A black hole is a region of space where the gravitational pull is so strong that not even light can escape.", x=0, y=0, node_types=["concept"])
    node2_id = db.add_node(question="How are black holes formed?", answer="Black holes are formed when massive stars collapse under their own gravity at the end of their life cycle.", x=1, y=0, node_types=["formation"])
    node3_id = db.add_node(question="What is the event horizon?", answer="The event horizon is the boundary surrounding a black hole beyond which nothing can escape.", x=0, y=1, node_types=["structure"])
    node4_id = db.add_node(question="What is the singularity?", answer="The singularity is the point at the center of a black hole where gravity is thought to be infinite.", x=1, y=1, node_types=["structure"])

    # You can add edges if needed to represent relationships between these concepts.
    # For example, linking the concept of a black hole to its formation:

    db.add_edge(source_id=node1_id, target_id=node2_id, edge_types=["related_to"])
    db.add_edge(source_id=node1_id, target_id=node3_id, edge_types=["contains"])
    db.add_edge(source_id=node3_id, target_id=node4_id, edge_types=["contains"])

    # Don't forget to close the database connection when you're done
    db.close()
    print('ok')