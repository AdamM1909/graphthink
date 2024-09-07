#   docker run \
#   --name neo4j \
#   -p 7474:7474 -p 7687:7687 \
#   -v ~/neo4j/data:/data \
#   -v ~/neo4j/logs:/logs \
#   -e NEO4J_AUTH=neo4j/password \
#   -e NEO4J_PLUGINS='["graph-data-science"]' \
#   -d neo4j:latest
# http://localhost:7474/browser/
# graph deck

from neo4j import GraphDatabase

__all__ = ['GraphDB']

class GraphDB:
    def __init__(self, uri="bolt://localhost:7687", username="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
    def add_node(self, question, answer, node_tags) -> int: 
        with self.driver.session() as session:
            return self.driver.execute_query("""CREATE (n:Node {question: $question, answer: $answer, node_tags: $node_tags}) RETURN id(n) as node_id""", 
                                               dict(question=question, answer=answer, node_tags=node_tags),
                                               result_transformer_=lambda r: r.single(strict=True))["node_id"]

    def add_edge(self, from_id, to_id, edge_tags) -> int:
         with self.driver.session() as session:
             return self.driver.execute_query("""MATCH (a) WHERE id(a) = $from_id MATCH (b) WHERE id(b) = $to_id CREATE (a)-[r:RELATED_TO {edge_tags: $edge_tags}]->(b)""", 
                                               dict(from_id=from_id, to_id=to_id, edge_tags=edge_tags))

    def get_schedule(self):
        # dummy schedule for the moment 
        with self.driver.session() as session:
            result = session.run("MATCH (n:Node) RETURN id(n) as id ORDER BY id(n)")
            return [r['id'] for r in result]
    
    def get_card_by_id(self, id: int):
        with self.driver.session() as session:
            result = session.run("MATCH (n) WHERE id(n) = $id RETURN n.question as question, n.answer as answer", id=id)
            return result.single().data()
        
    def __enter__(self): return self
    def __exit__(self, *args): self.close() 
    def close(self): 
        if self.driver is not None: self.driver.close()
               