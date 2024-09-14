from functools import lru_cache
from backend.db import *
from fasthtml.common import *


app, rt = fast_app()

with GraphDB() as db:
    deck_qs = {r['n.deck_name']: r['nodes'] for r in db.q("MATCH (n)  RETURN n.deck_name, collect(n) AS nodes").records}

def make_dropdown(name, options): return (Option(f'-- select {name} --', disabled='', selected='', value=''), *map(Option, options))
def make_node_selection_column(to_from):  
    deck_dropdown = Select(*make_dropdown('deck', list(deck_qs.keys())), name='deck', hx_get='/questions', hx_target=f'#questions_{to_from}')
    question_dropdown = Select(id=f'questions_{to_from}')
    return  Div(Div(deck_dropdown),Div(question_dropdown))

@rt('/')
def homepage():
    return Div(
        Style("""
              .container {display: flex; width: 100%; justify-content: space-between;}
              .column {width: 48%; padding: 20px; box-sizing: border-box;}
              """),
        Div(
            Div(H2("Connect From"), make_node_selection_column('from'), cls="column"),
            Div(H2("Connect To"), make_node_selection_column('to'), cls="column"),
            cls="container"
        )
    )
   
@rt('/questions')
@lru_cache(maxsize=None)
def questions_in_deck(deck: str): return make_dropdown('flashcard', [node['question'] for node in deck_qs[deck]])
    
serve()