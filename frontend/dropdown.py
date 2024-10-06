from fasthtml.common import *
from backend.db import *

app, rt = fast_app()

def get_tags():
    with GraphDB() as db:
        return [r['tag'] for r in db.q("MATCH ()-[r]->() UNWIND r.relationship_tags AS tag RETURN DISTINCT tag").records]

@rt('/')
def get(): 
    checkbox_form = Form(*[CheckboxX(id=tag, label=tag) for tag in get_tags()], id='checkbox_form')
    submit_btn = Button("Submit", id='submit_btn', hx_post="/submit", hx_target="#result", hx_include='#checkbox_form')
    new_tag_input = Input(id="new_tag", placeholder="Add new relationship type")
    add_new_tag_btn = Button("Add New", hx_post="/add_tag", hx_target="#checkbox_form", hx_swap='beforeend', hx_include='#new_tag')
    return Div(checkbox_form, Div(new_tag_input, add_new_tag_btn, submit_btn), Div(id="result"))

@rt('/add_tag')
def add_tag(tag: dict):
    new_checkbox = CheckboxX(id=tag["new_tag"], label=tag["new_tag"], checked=True)
    refreshed_new_tag_input = Input(id="new_tag", placeholder="Add new relationship type", hx_swap_oob="true")
    return new_checkbox, refreshed_new_tag_input

@app.post('/submit')
def submit(checkbox_form: dict): return ', '.join((k for k, v in checkbox_form.items() if isinstance(v, list)))


serve()


# @rt('/add_option')
# def post(new_option: str):
#     new_checkbox = CheckboxX(id=f"option-{new_option}", label=new_option, name="options", value=new_option, checked=True)
#     reset_input = Input(id="new-option", name="new_option", placeholder="or add new relationship type", value="", hx_swap_oob="true")
#     return new_checkbox, reset_input
