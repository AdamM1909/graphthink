from fasthtml.common import *
from backend.db import *

app, rt = fast_app()

def get_tags():
    with GraphDB() as db:
        return [r['tag'] for r in db.q("MATCH ()-[r]->() UNWIND r.relationship_tags AS tag RETURN DISTINCT tag").records]

@rt('/')
def get(): 
    checkbox_form = Form(
                    *[CheckboxX(id=tag, label=tag) for tag in get_tags()],
                    Button("Submit", id='submit_btn', hx_post="/submit", hx_target="#result", hx_include='#checkbox_form'),
                    id='checkbox_form'
                     )
 
    new_tag_input = Input(id="new_tag", placeholder="Add new relationship type")
    add_new_tag_button = Button("Add New", hx_post="/add_tag", hx_target="#submit_btn", hx_swap='beforebegin', hx_include='#new_tag')
    
    
    return Div(checkbox_form, Div(new_tag_input, add_new_tag_button), Div(id="result"))
    
    
@app.post('/submit')
def submit(checkbox_form: dict):
    checkbox_form.pop('submit_btn')
    return ', '.join((k for k, v in checkbox_form.items() if isinstance(v, list)))
    

@rt('/add_tag')
def add_tag(tag: dict): return CheckboxX(id=tag["new_tag"], label=tag["new_tag"], checked=True)
 

serve()