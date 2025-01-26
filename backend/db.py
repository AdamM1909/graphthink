from neo4j import GraphDatabase, EagerResult
from anki.collection import Collection
from dotenv import load_dotenv
import os 


__all__ = ['GraphDB', 'AnkiDB']
load_dotenv()
ANKI_DB_PATH, NEO4JURI, NEO4JUSR, NEO4JPASS = os.getenv('ANKI_DB_PATH'), os.getenv('NEO4JURI'), os.getenv('NEO4JUSR'), os.getenv('NEO4JPASS')


# Nomenclature:
# v, vs   : vertex/vertices (flashcards)
# e, es   : edge/edges (relationships)
# id      : vertex id
# uid,vid : source/target vertex ids
# tags    : edge / vertex tags
# ns      : anki notes
# q       : question
# a       : answer 
# d       : deck


class GraphDB:
    def __init__(self, uri=NEO4JURI, username=NEO4JUSR, password=NEO4JPASS):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    def add_vertex(self, id: int, q: str, a: str, d: str, tags: list): self.q("MERGE (v {id: $id}) SET v.q = $q, v.a = $a, v.d = $d, v.tags = $tags", dict(id=id, q=q, a=a, d=d, tags=tags))
    def add_edge(self, uid: int, vid: int, tags: list = None):
        if uid == vid: return
        self.q("""MATCH (u {id: $uid}), (v {id: $vid}) MERGE (u)-[ {tags: $tags}]->(v)""", dict(uid=uid, vid=vid, tags=tags or []))
    def setup(self): self.q("CREATE INDEX id IF NOT EXISTS FOR (v) ON (v.id)")     
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
    
def anki2graphsync(adb, gdb):
    ns = []
    for d in adb.collection.decks.all_names_and_ids():
        if 'GraphThink' not in d.name: continue
        for nid in adb.collection.find_notes(f"did:{d.id}"):
            n = adb.collection.get_note(nid)
            ns.append(dict(id=n.id, q=n.fields[0], a=n.fields[1], d=adb.deck_name(n.id), tags=n.tags))
    
    fields = list(ns[0].keys())
    sql = f"""
        UNWIND $ns AS n
        MERGE (v {{id: n.id}})
        ON CREATE SET {','.join(f'v.{f}=n.{f}' for f in fields)}
        ON MATCH SET {','.join(f'v.{f}=CASE WHEN v.{f}<>n.{f} THEN n.{f} ELSE v.{f} END' for f in fields)}
        RETURN v"""

    res = gdb.driver.session().write_transaction(lambda tx, ns: tx.run(sql, ns=ns).data(), ns)
    gdb.q("MATCH (v) WHERE NOT v.id IN $ids DETACH DELETE v", dict(ids=[n['id'] for n in ns]))
    assert len(res) == len(ns), f"Vertex count mismatch: Neo4j={len(res)} Anki={len(ns)}"

 