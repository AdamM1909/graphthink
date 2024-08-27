import sqlite3

__all__ = ['GraphDB']
class GraphDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def add_node(self, question, answer, x, y, node_types=[]):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO nodes (question, answer, x, y) VALUES (?, ?, ?, ?)", (question, answer, x, y))
        node_id = cursor.lastrowid
        for node_type in node_types: cursor.execute("INSERT INTO node_type_associations (node_id, type_id) VALUES (?, ?)", (node_id, self._get_id('node_type',node_type)))
        self.conn.commit()
        return node_id
    
    def add_edge(self, source_id, target_id, edge_types=[]):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO edges (source_id, target_id) VALUES (?, ?)", (source_id, target_id))
        edge_id = cursor.lastrowid
        for edge_type in edge_types: cursor.execute("INSERT INTO edge_type_associations (edge_id, type_id) VALUES (?, ?)", (edge_id, self._get_id('edge_type', edge_type)))
        self.conn.commit()
        return edge_id
    
    def get_subgraph(self, node_conditions=[], edge_conditions=[], node_logic="AND", edge_logic="AND"):
        def part_subquery(part, conditions, logic):
            if conditions:
                subquery = f"""
                    SELECT {part}_id 
                    FROM {part}_type_associations 
                    WHERE type_id IN (
                        SELECT id FROM {part}_types WHERE name IN ({",".join("?" for _ in conditions)})
                    )
                    GROUP BY {part}_id
                    HAVING COUNT(DISTINCT type_id) {'=' if logic == "AND" else '>'} {len(conditions) if logic == "AND" else 0}
                """
                return f"{part}.id IN ({subquery})" 
            return None

        edge_query, node_query = part_subquery('edge', edge_conditions, edge_logic), part_subquery('ndoe', node_conditions, node_logic)

        query = f"""
            WITH FilteredNodes AS (
                SELECT node.id, node.question, node.answer, node.x, node.y
                FROM nodes node
                {"WHERE " + node_query if node_query else ""}
            )
            SELECT DISTINCT edge.id, edge.source_id, edge.target_id, fn_source.id AS source_node_id, fn_target.id AS target_node_id
            FROM edges edge
            JOIN FilteredNodes fn_source ON edge.source_id = fn_source.id
            JOIN FilteredNodes fn_target ON edge.target_id = fn_target.id
            {"WHERE " + edge_query if edge_query else ""}
        """

        cursor = self.conn.execute(query, [*node_conditions, *edge_conditions])
        edges = cursor.fetchall()

        # Extracting the unique nodes from the edges
        node_ids = set()
        for edge in edges:
            node_ids.add(edge[3])  # source_node_id
            node_ids.add(edge[4])  # target_node_id

        # Query to fetch the node details
        if node_ids:
            nodes_query = f"""
                SELECT id, question, answer, x, y
                FROM nodes
                WHERE id IN ({",".join("?" for _ in node_ids)})
            """
            nodes_cursor = self.conn.execute(nodes_query, list(node_ids))
            nodes = nodes_cursor.fetchall()
        else:
            nodes = []

        # Return nodes and edges separately
        return nodes, edges
        
    def get_types(self, part, id):
        assert part in ['node', 'edge']
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT nt.name FROM {part}_type_associations nta JOIN node_types nt ON nta.type_id = nt.id WHERE nta.id = ?", (id,))
        return [row[0] for row in cursor.fetchall()]
         
    def close(self):
        self.conn.close()
    
    def _get_id(self, table, name):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT id FROM {table} WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result[0] if result else self._add_into(table, name)
    
    def _add_into(self, table, name):
        cursor = self.conn.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO {table} (name) VALUES (?)", (name,))
        self.conn.commit()
        return cursor.lastrowid
       
    
    def _create_tables(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, question TEXT, answer TEXT, x INTEGER, y INTEGER)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS node_types (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS edges (id INTEGER PRIMARY KEY, source_id INTEGER, target_id INTEGER, FOREIGN KEY (source_id) REFERENCES nodes (id), FOREIGN KEY (target_id) REFERENCES nodes (id))")
        self.conn.execute("CREATE TABLE IF NOT EXISTS edge_types (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS node_type_associations (node_id INTEGER, type_id INTEGER, FOREIGN KEY (node_id) REFERENCES nodes (id), FOREIGN KEY (type_id) REFERENCES node_types (id), PRIMARY KEY (node_id, type_id))")
        self.conn.execute("CREATE TABLE IF NOT EXISTS edge_type_associations (edge_id INTEGER, type_id INTEGER, FOREIGN KEY (edge_id) REFERENCES edges (id), FOREIGN KEY (type_id) REFERENCES edge_types (id), PRIMARY KEY (edge_id, type_id))")
        # self.conn.execute("CREATE INDEX IF NOT EXISTS idx_node_type_associations_node_id ON node_type_associations(node_id)")
        # self.conn.execute("CREATE INDEX IF NOT EXISTS idx_node_type_associations_type_id ON node_type_associations(type_id)")
        # self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edge_type_associations_edge_id ON edge_type_associations(edge_id)")
        # self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edge_type_associations_type_id ON edge_type_associations(type_id)")
        # self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_source_id ON edges(source_id)")
        # self.conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_target_id ON edges(target_id)")
        self.conn.commit()
        
if __name__ == '__main__':
    # Create an instance of GraphDB
    db = GraphDB('black_holes.sqlite')
    if False:
        # Add nodes (flashcards) about black holes
        node1_id = db.add_node(question="What is a black hole?", answer="A black hole is a region of space where the gravitational pull is so strong that not even light can escape.", x=0, y=0, node_types=["concept"])
        node2_id = db.add_node(question="How are black holes formed?", answer="Black holes are formed when massive stars collapse under their own gravity at the end of their life cycle.", x=1, y=0, node_types=["formation"])
        node3_id = db.add_node(question="What is the event horizon?", answer="The event horizon is the boundary surrounding a black hole beyond which nothing can escape.", x=0, y=1, node_types=["structure"])
        node4_id = db.add_node(question="What is the singularity?", answer="The singularity is the point at the center of a black hole where gravity is thought to be infinite.", x=1, y=1, node_types=["structure"])

        db.add_edge(source_id=node1_id, target_id=node2_id, edge_types=["related_to"])
        db.add_edge(source_id=node1_id, target_id=node3_id, edge_types=["contains", "related_to"])
        db.add_edge(source_id=node3_id, target_id=node4_id, edge_types=["contains"])
    print('ok')
    db.close()