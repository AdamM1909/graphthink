from fasthtml.common import *
from backend.db import *

app, rt = fast_app()

# @rt('/')
# def get():
#     with GraphDB() as db:
#         tags = [r['tag'] for r in db.q("MATCH ()-[r]->() UNWIND r.relationship_tags AS tag RETURN DISTINCT tag").records]
    
#     check_tags = Div(*[CheckboxX(id=f"option-{t}", label=t, name="options", value=t) for t in tags], id="checkbox-group")
    
#     new_tags = Form(
#         Input(id="new-option", name="new_option", placeholder="or add new realtionship type"),
#         Button("Add", hx_post="/add_option", hx_target="#checkbox-group", hx_swap="beforeend"),
#     )
#     form = Form(H2("Select options:"), check_tags, new_tags, 
#                 Button("Submit", hx_post="/submit", hx_target="#result"),
#                 Div(id="result") )

#     return Titled("Multi-Select Form", form)

# @rt('/add_option')
# def post(new_option: str):
#     new_checkbox = CheckboxX(id=f"option-{new_option}", label=new_option, name="options", value=new_option, checked=True)
#     reset_input = Input(id="new-option", name="new_option", placeholder="or add new realtionship type", value="", hx_swap_oob="true")
#     return new_checkbox, reset_input

# @rt('/submit')
# def abc(options: list[str] = []):
#     return Div(f"You selected: {', '.join(options)}", id="result")




# @rt("/")
# def get():
#     form = Form(
#         Input(id="name", name="name", placeholder="Enter your name"),
#         Input(id="age", name="age", type="number", placeholder="Enter your age"),
#         Button("Submit", type="submit"),
#         hx_post="/submit",
#         hx_trigger="submit",  # Changed to trigger on form submit
#         hx_target="#result"
#     )

#     main_content = Div(
#         H1("Form Submission Example"),
#         form,
#         Div(id="result")
#     )

#     return Titled("FastHTML Form Example", main_content)

# @rt("/submit")
# async def post(name: str, age: int):
#     # Process the form data here
#     result = f"Server received: Name - {name}, Age - {age}"
#     return Div(result, id="result")


@rt('/')
def get():
    with GraphDB() as db:
        tags = [r['tag'] for r in db.q("MATCH ()-[r]->() UNWIND r.relationship_tags AS tag RETURN DISTINCT tag").records]
    
    check_tags = Div(*[CheckboxX(id=f"option-{t}", label=t, name="options", value=t) for t in tags], id="checkbox-group")
    
    new_tags = Form(
        Input(id="new-option", name="new_option", placeholder="or add new relationship type"),
        Button("Add", hx_post="/add_option", hx_target="#checkbox-group", hx_swap="beforeend"),
    )
    form = Form(
        H2("Select options:"), 
        check_tags, 
        new_tags, 
        Button("Submit", type="submit"),
        hx_post="/submit", 
        hx_target="#result",
        hx_trigger="submit"
    )
    
    main_content = Div(
        form,
        Div(id="result")
    )

    return Titled("Multi-Select Form", main_content)

@rt('/add_option')
def post(new_option: str):
    new_checkbox = CheckboxX(id=f"option-{new_option}", label=new_option, name="options", value=new_option, checked=True)
    reset_input = Input(id="new-option", name="new_option", placeholder="or add new relationship type", value="", hx_swap_oob="true")
    return new_checkbox, reset_input

@rt("/submit")
async def post(options: list = None):
    if options is None:
        options = []
    result = f"Selected options: {', '.join(options)}"
    return Div(result, id="result")

serve()

# serve()
