from neo4j import GraphDatabase, EagerResult
from anki.collection import Collection
from dotenv import load_dotenv
import os 


__all__ = ['GraphDB']
load_dotenv()
ANKI_DB_PATH, NEO4JURI, NEO4JUSR, NEO4JPASS = os.getenv('ANKI_DB_PATH'), os.getenv('NEO4JURI'), os.getenv('NEO4JUSR'), os.getenv('NEO4JPASS')


class GraphDB:
    def __init__(self, uri=NEO4JURI, username=NEO4JUSR, password=NEO4JPASS):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
    def add_edge(self, from_note_id, to_note_id, edge_tags) -> None:
        return self.q("""MATCH (from) WHERE from.note_id = $from_note_id MATCH (to) WHERE to.note_id = $to_note_id CREATE (from)-[r:RELATED_TO {edge_tags: $edge_tags}]->(to)""",
                            dict(from_note_id=from_note_id, to_note_id=to_note_id, edge_tags=edge_tags))
        
    def sync_anki(self): 
        with ADB() as adb:
            notes = {id: adb.collection.get_note(id) for id in adb.collection.find_notes("")}
            anki_data = [dict(note_id=note.id, question=note.fields[0], answer=note.fields[1], deck_name=adb.deck_name(note.id), tags=note.tags) for note in notes.values()]

        with self.driver.session() as session:
            sql = f"""
                UNWIND $node_data AS data
                MERGE (n:Node {{note_id: data.note_id}})
                ON CREATE SET
                    {','.join([f"n.{f} = data.{f}" for f in anki_data[0].keys()])}
                ON MATCH SET
                    {','.join([f"n.{f} = CASE WHEN n.{f} <> data.{f} THEN data.{f} ELSE n.{f} END" for f in anki_data[0].keys()])}
                RETURN n
                """
            result = session.write_transaction(lambda tx, anki_data: tx.run(sql, node_data=anki_data).data() , anki_data)
        
        self.q("""MATCH (n:Node) WHERE NOT n.note_id IN $note_ids DETACH DELETE n""", dict(note_ids=list(notes.keys())))
        assert (ngdb := len(result)) == (nanki := len(notes)), "Number of cards in anki and neo4j do not match, Anki has {nanki} GraphDB has {ngdb}."

    def q(self, sql: str, params = None) -> EagerResult: return self.driver.execute_query(sql, params)
                   
    def setup(self): self.q("CREATE INDEX note_id IF NOT EXISTS FOR (n:Node) ON (n.note_id)")   
    def close(self): 
        if self.driver is not None: self.driver.close()
    def __enter__(self): return self
    def __exit__(self, *args): self.close() 
    
class ADB():
    def __init__(self, path=ANKI_DB_PATH):
        self.collection = Collection(path)

    def deck_name(self, note_id):
        card_ids = self.collection.find_cards(f"nid:{note_id}")
        return self.collection.decks.name(self.collection.get_card(card_ids[0]).did)
    
    def close(self): 
        if self.collection is not None: self.collection.close()
    def __enter__(self): return self
    def __exit__(self, *args): self.close() 
 