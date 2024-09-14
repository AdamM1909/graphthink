from fasthtml.common import *
from backend.db import *

app, rt = fast_app()

@rt('/')
def get():
    with GraphDB() as db:
        options = [r['n.deck_name'] for r in db.q("MATCH (n) RETURN DISTINCT n.deck_name").records]
    
    checkbox_group = Div(
        *[CheckboxX(id=f"option-{opt}", label=opt, name="options", value=opt) for opt in options],
        id="checkbox-group"
    )
    
    new_option_form = Form(
        Input(id="new-option", name="new_option", placeholder="New option"),
        Button("Add", hx_post="/add-option", hx_target="#checkbox-group", hx_swap="beforeend"),
        id="new-option-form"
    )
    
    submit_button = Button("Submit", type="submit")
    
    form = Form(
        H2("Select options:"),
        checkbox_group,
        H3("Add a new option:"),
        new_option_form,
        submit_button,
        hx_post="/submit", hx_target="#result"
    )
    
    result_div = Div(id="result")
    
    return Titled("Multi-Select Form", form, result_div)

@rt('/add-option')
def post(new_option: str):
    new_checkbox = CheckboxX(id=f"option-{new_option}", label=new_option, name="options", value=new_option, checked=True)
    reset_input = Input(id="new-option", name="new_option", placeholder="New option", value="", hx_swap_oob="true")
    return new_checkbox, reset_input

@rt('/submit')
def post(options: list[str] = []):
    return f"You selected: {', '.join(options)}"

serve()
