# docker run \     
# --name neo4j \
# -p 7474:7474 -p 7687:7687 \
# -v ~/neo4j/data:/data \
# -v ~/neo4j/logs:/logs \
# -e NEO4J_AUTH=neo4j/password \
# -d neo4j:latest
# http://localhost:7474/browser/

from neo4j import GraphDatabase

__all__ = ['GraphDB']

class GraphDb:
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

    def __enter__(self): return self
    def __exit__(self, *args): self.close() 
    def close(self): 
        if self.driver is not None: self.driver.close()


if __name__ == "__main__":
    
    with  GraphDb() as db:
        id0 = db.add_node("What is a black hole?", 
                          "A black hole is a region of space where the gravitational pull is so strong that not even light can escape.", 
                          ["concept"])
        
        id1 = db.add_node("How are black holes formed?", 
                          "Black holes are formed when massive stars collapse under their own gravity at the end of their life cycle.", 
                          ["formation", "concept"])
        
        id2 = db.add_node("What is the event horizon?", 
                          "The event horizon is the boundary surrounding a black hole beyond which nothing can escape.", 
                          ["structure"])
        
        id3 = db.add_node("What is the singularity?", 
                          "The singularity is the point at the center of a black hole where gravity is thought to be infinite.", 
                          ["structure", "concept"])
        
        id4 = db.add_node("What are the two numbers which describe a Kerr black hole?", 
                          "Mass and spin", 
                          ["concept", "spinning"])
        
        db.add_edge(id0, id1, ["related_to"])
        db.add_edge(id0, id3, ["deeper", "related_to"])
        db.add_edge(id0, id2, ["deeper", "related_to"])
        db.add_edge(id2, id4, ["related_to", "simple"])
        db.add_edge(id1, id0, ["related_to", "simple"])
        db.add_edge(id4, id3, ["simple"])
        

        
      
        