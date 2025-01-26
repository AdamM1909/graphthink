from backend.db import *

def anki2graphsync(adb, gdb):
    ns = []
    for d in adb.collection.decks.all_names_and_ids():
        if 'GraphThink' not in d.name: continue
        for nid in adb.collection.find_notes(f"did:{d.id}"):
            n = adb.collection.get_note(nid)
            ns.append(dict(id=n.id, q=n.fields[0], a=n.fields[1], d=adb.deck_name(n.id), tags=n.tags))
    
    gdb.q(f"""
        UNWIND $ns AS n
        MERGE (v:V {{id: n.id}})
        ON CREATE SET {','.join(f'v.{f}=n.{f}' for f in VERTEX_FIELDS)}
        ON MATCH SET {','.join(f'v.{f}=CASE WHEN v.{f}<>n.{f} THEN n.{f} ELSE v.{f} END' for f in VERTEX_FIELDS)}
        RETURN v""", dict(ns=ns))
    gdb.q("MATCH (v:V) WHERE NOT v.id IN $ids DETACH DELETE v", dict(ids=[n['id'] for n in ns]))
    
    assert (n := gdb.q("MATCH (v:V) RETURN count(v) as n")[0][0]["n"]) == len(ns), f"Vertex count mismatch: Neo4j={n} Anki={len(ns)}"
    
    
def make_anki_deck(adb, vs, deck_name):
    did, model  = adb.collection.decks.id(deck_name, create=True), adb.collection.models.byName("Basic")
    for f, b in vs:
        note = adb.collection.new_note(model)
        note.fields = [f, b]
        adb.collection.add_note(note, did)