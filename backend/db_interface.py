import sqlite3
from dataclasses import dataclass
from typing import Literal

__all__ = ['GraphDB']

@dataclass
class Part:
    type: Literal['node', 'edge']
    
    
class GraphDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def add_node(self, question, answer, x, y, node_types=[]):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO nodes (question, answer, x, y) VALUES (?, ?, ?, ?)", (question, answer, x, y))
        node_id = cursor.lastrowid
        for node_type in node_types: cursor.execute("INSERT INTO node_type_associations (node_id, type_id) VALUES (?, ?)", (node_id, self._get_id('node_types', node_type)))
        self.conn.commit()
        return node_id
    
    def add_edge(self, source_id, target_id, edge_types=[]):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM edges WHERE source_id = ? AND target_id = ?", (source_id, target_id))
        assert not cursor.fetchone()[0], "Edge already exists."
        cursor.execute("INSERT INTO edges (source_id, target_id) VALUES (?, ?)", (source_id, target_id))
        edge_id = cursor.lastrowid
        for edge_type in edge_types: cursor.execute("INSERT INTO edge_type_associations (edge_id, type_id) VALUES (?, ?)", (edge_id, self._get_id('edge_types', edge_type)))
        self.conn.commit()
        return edge_id
    
    def delete_part(self, p, id):
        cursor = self.conn.cursor()
        self.conn.execute(f"DELETE FROM {p}_type_associations WHERE node_id = ?", (id,))
        self.conn.execute(f"DELETE FROM {p}s WHERE id = ?", (id,))
        self.conn.execute(f"""DELETE FROM {p}_types WHERE id NOT IN (SELECT type_id FROM {p}_type_associations)""")
        if p == 'node': [self.delete_part(p='edge', id=eid) for eid in self.conn.execute("SELECT id FROM edges WHERE source_id = ? OR target_id = ?", (id, id)).fetchall()]
           
    def get_subgraph(self, node_types=[], edge_types=[], node_logic="AND", edge_logic="AND"):
        assert edge_logic in ['AND', 'OR']
        assert node_logic in ['AND', 'OR']
        def part_subquery(p, conditions=[], logic="AND"):
            if conditions:
                subquery = f"""
                    SELECT {p}_id FROM {p}_type_associations 
                    WHERE type_id IN (SELECT id FROM {p}_types WHERE name IN ({",".join("?" for _ in conditions)}))
                    GROUP BY {p}_id
                    HAVING COUNT(DISTINCT type_id) {'=' if logic == "AND" else '>='} {len(conditions) if logic == "AND" else 1}
                """
                return f"{p}.id IN ({subquery})"
            return '1=1'
        node_query, edge_query = part_subquery('node', node_types, node_logic), part_subquery('edge', edge_types, edge_logic)
        query = f"""
            SELECT DISTINCT node.id as node_id, edge.id as edge_id
            FROM nodes node
            JOIN edges edge ON (node.id = edge.source_id OR node.id = edge.target_id)
            WHERE ({node_query}) AND ({edge_query})
        """
        cursor = self.conn.execute(query, [*node_types, *edge_types])
        results = cursor.fetchall()
        nodes, edges = list(set(r['node_id'] for r in results)), list(set(r['edge_id'] for r in results))
        return nodes, edges if len(nodes) > 1 else []
      
    def get_types(self, part, id):
        assert part in ['node', 'edge']
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT nt.name FROM {part}_type_associations nta JOIN node_types nt ON nta.type_id = nt.id WHERE nta.id = ?", (id,))
        return [row[0] for row in cursor.fetchall()]
         
    def close(self): self.conn.close()
    
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
        self.conn.commit()
        
