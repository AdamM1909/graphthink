from fasthtml.common import *
from backend.db import GraphDB

app, rt = fast_app(debug=True)
db = GraphDB()

@rt('/')
def get():
    return Titled("Flashcard Study",
        Main(
            P("Click the button below to start your study session."),
            Button("Begin Study", hx_get="/study", hx_push_url="true", hx_target="body"))
    )
    
# / / / / / / / / / Study / / / / / / / / / #

@rt('/study')
def get_study(session):
    session["schedule"], session["schedule_idx"]  = db.get_schedule(), 0
    return Main(
        Div(Button("Back to Home", hx_get="/", hx_push_url="true", hx_target="body"), id="back-to-home-button", style="position: absolute; top: 10px; left: 10px;"),
        Div(id="flashcard-container", style="padding-top: 30px; text-align: center;"),
        Div(id="button-container",style="position: fixed; bottom: 10%; left: 0; right: 0; text-align: center;"),
        Script(f"htmx.ajax('GET', '/study/card/', {{target:'#flashcard-container'}})")
    )
    
@rt('/study/card/')
def get_card(session):
    session["current_card"] = db.get_card_by_id(session["schedule"][session["schedule_idx"]])
    return (
        Div(P(session["current_card"]["question"], style="text-align: center;"), style="text-align: center;", id="flashcard-container"),
        Div(Button("Reveal Answer", hx_get=f"/study/card/reveal", hx_target="#flashcard-container"), hx_swap_oob="innerHTML", id="button-container")
        )

@rt('/study/card/reveal')
def get_reveal_answer(session):
    if (session["schedule_idx"] + 1) == len(session["schedule"]): session["schedule_idx"] = None
    else: session["schedule_idx"] += 1 
    return (
        Div(
            P(session["current_card"]["question"], style="text-align: center; margin-bottom: 5px;"),
            Div(Hr(style="border: 0; height: 1px; background: #ccc; width: 70%;"), style="display: flex; justify-content: center;"),
            P(session["current_card"]["answer"], style="text-align: center; margin-top: 5px;"),
            style="text-align: center;",
            id="flashcard-container"
        ),
        Div(
            Button("Next Flashcard" if session["schedule_idx"] else "Complete Session", 
                   hx_get=f"/study/card/" if session["schedule_idx"] else "/study/complete",
                   hx_target="#flashcard-container"),
            hx_swap_oob="innerHTML",
            id="button-container"
        )
    )
    
@rt('/study/complete')
def get_study_complete():
    return Main(
        Div(
            P("Well done! You've gone through all the flashcards.", style="text-align: center; margin-bottom: 50px;"),
            Button("Back to Home", hx_get="/", hx_push_url="true", hx_target="body"), style="text-align: center;"),
        Div(hx_swap_oob="delete", id="button-container"),
        Div(hx_swap_oob="delete", id="back-to-home-button")
        )
    
# / / / / / / / / / Connect / / / / / / / / / #
    

serve()