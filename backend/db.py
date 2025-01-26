from neo4j import GraphDatabase, EagerResult
from anki.collection import Collection
from dotenv import load_dotenv
import os 


__all__ = ['GraphDB', 'AnkiDB', 'VERTEX_FIELDS']
load_dotenv()
ANKI_DB_PATH, NEO4JURI, NEO4JUSR, NEO4JPASS = os.getenv('ANKI_DB_PATH'), os.getenv('NEO4JURI'), os.getenv('NEO4JUSR'), os.getenv('NEO4JPASS')

# Nomenclature:
# (u, v), vs   : vertex/vertices (flashcards)
# e, es   : edge/edges (relationships)
# id      : id
# q       : question
# a       : answer 
# d       : deck
# tags    : edge / vertex tags

VERTEX_FIELDS = ['id', 'q', 'a', 'd', 'tags']
class GraphDB:
    def __init__(self, uri=NEO4JURI, username=NEO4JUSR, password=NEO4JPASS):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.q("CREATE INDEX id IF NOT EXISTS FOR (v:V) ON (v.id)")
    def add_edge(self, uid: int, vid: int, tags: list = None):
        if uid == vid: return
        self.q("""MATCH (u {id: $uid}), (v {id: $vid}) MERGE (u)-[ {tags: $tags}]->(v)""", dict(uid=uid, vid=vid, tags=tags or []))     
    def id_from_q(self, q: str) -> int: return self.q("MATCH (v:V) WHERE v.q CONTAINS $q RETURN v.id", dict(q=q))[0][0]
    def q(self, sql: str, params: dict = None) -> EagerResult: return self.driver.execute_query(sql, params)                
    def close(self): 
        if self.driver is not None: self.driver.close()
    def __enter__(self): return self
    def __exit__(self, *args): self.close()
    

class AnkiDB():
    def __init__(self, path = ANKI_DB_PATH):
        self.collection = Collection(path)
    def deck_name(self, id): return self.collection.decks.name(self.collection.get_card(self.collection.find_cards(f"nid:{id}")[0]).did)
    def close(self): 
        if self.collection is not None: self.collection.close()
    def __enter__(self): return self
    def __exit__(self, *args): self.close()
 