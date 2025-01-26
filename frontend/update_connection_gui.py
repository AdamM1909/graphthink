from functools import lru_cache
from backend.db import *
from fasthtml.common import *

custom_styles = """
<style>
    .select_pair_gui {display: flex; width: 100%; justify-content: space-between;}
    .select_pair_gui_card_column {width: 48%; padding: 20px; box-sizing: border-box;}
    .update_connection_gui {width: 100%; max-width: 600px; margin: 0 auto; padding: 20px; box-sizing: border-box;}
    .update_connection_gui form {margin-bottom: 20px;}
    .update_connection_gui input[type="text"], .update_connection_gui #submit_btn {width: 100%; margin-bottom: 10px;}
    .update_connection_gui #submit_btn {margin-top: 20px;}
    .update_connection_gui_checkboxes {display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding: 5px; border-radius: 5px;}
    .update_connection_gui_checkboxes label {flex-grow: 1; margin-right: 10px;}
    .update_connection_gui_checkboxes input[type="checkbox"] {width: 16px; height: 16px; margin: 0; padding: 0;}
    
    
    .update_connection_gui_new_tag_input {display: flex; justify-content: space-between; align-items: stretch; margin-bottom: 10px;}
    .update_connection_gui_new_tag_input input {flex-grow: 1; margin-right: 10px; height: 38px; padding: 0 10px; box-sizing: border-box;}
    .update_connection_gui_new_tag_input button {width: auto; padding: 0 15px; height: 38px; box-sizing: border-box;}
    .update_connection_submit_btn button {border: 0.5px solid transparent;}
    .update_connection_submit_btn button:hover {border-color: white;}
</style>
"""

app, rt = fast_app(pico=True, hdrs=(NotStr(custom_styles),))


# TODO: Make the tags of the currently selected pair be ticked by default:
#     tags = self.q("""
#         MATCH (from)-[r]->(to)
#         WHERE from.note_id = $from_note_id AND to.note_id = $to_note_id
#         RETURN r.relationship_tags AS tags
#     """, dict(from_note_id=from_note_id, to_note_id=to_note_id))

# --------- select_pair_gui --------- #

with GraphDB() as db:
    deck_qs = {r['n.d']: r['nodes'] for r in db.q("MATCH (n)  RETURN n.d, collect(n) AS nodes").records}


def mk_dropdown(name, options): 
    ops = map(lambda k: Option(k, value=options[k]), options) if isinstance(options, dict) else map(Option, options)
    return (Option(f'-- select {name} --', disabled='', selected='', value=''), *ops)


def mk_node_column(to_from):  
    deck_dropdown = Select(*mk_dropdown('deck', list(deck_qs.keys())), name='deck', hx_get='/questions_in_deck', hx_target=f'#note_id_{to_from}')
    question_dropdown = Select(id=f'note_id_{to_from}')
    return  Div(Div(deck_dropdown), Div(question_dropdown))

@rt('/questions_in_deck')
@lru_cache(maxsize=None)
def questions_in_deck(deck: str): 
    return mk_dropdown('flashcard', {node['question']: node['note_id'] for node in deck_qs[deck]})


def mk_select_pair_gui():
    return Div(
                Div(
                Div(H3("Connect From"), mk_node_column('from'), cls="select_pair_gui_card_column"),
                Div(H3("Connect To"), mk_node_column('to'), cls="select_pair_gui_card_column"),
                cls="select_pair_gui"
        )
    )   

# --------- update_connection_gui ---------

def get_tags():
    with GraphDB() as db:
        return [r['tag'] for r in db.q("MATCH ()-[r]->() UNWIND r.tags AS tag RETURN DISTINCT tag").records]

def mk_tag_gui(): 
    checkbox_form = Form(*[Div(Label(tag), CheckboxX(id=tag), cls="update_connection_gui_checkboxes") for tag in get_tags()], id='checkbox_form')
    submit_btn = Button("Update Connection", id='submit_btn', hx_post="/submit_tag_update", hx_target="#result", hx_include='#checkbox_form, #note_id_from, #note_id_to')
    new_tag_input = Input(id="new_tag", placeholder="Type to create new tag ...")
    add_new_tag_btn = Button("Create", hx_post="/add_tag", hx_target="#checkbox_form", hx_swap='beforeend', hx_include='#new_tag')
    return Div(
                Div(
                    H3("Update Connection Tags", style="text-align: center;"),
                    checkbox_form,
                    Div(new_tag_input, add_new_tag_btn, cls="update_connection_gui_new_tag_input"),
                    Div(submit_btn, cls="update_connection_submit_btn"),
                    Div(id="result"),
                    cls="update_connection_gui"
        )
    )

@rt('/add_tag')
def add_tag(tag: dict):
    new_checkbox = Div(Label(tag["new_tag"]), CheckboxX(id=tag["new_tag"], checked=True), cls="update_connection_gui_checkboxes")
    refreshed_new_tag_input = Input(id="new_tag", placeholder="Type to create new tag ...", hx_swap_oob="true")
    return new_checkbox, refreshed_new_tag_input

@app.post('/submit_tag_update')
def submit_tag_update(d: dict): 
    tags = [k for k, v in d.items() if isinstance(v, list)] # Checked tags are lists.
    with GraphDB() as db:
        db.add_edge(int(d['note_id_from']), int(d['note_id_to']), tags)
    return ', '.join(tags)

# --------- homepage ---------

@rt('/')
def homepage(): return Div(mk_select_pair_gui(), mk_tag_gui())
   
    
serve()