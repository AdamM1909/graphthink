from fasthtml.common import *
from backend.db import GraphDB

app, rt = fast_app()
db = GraphDB()  # Initialize the Neo4j database connection

@rt('/')
def get():
    return Titled("Flashcard Study",
        Main(
            P("Click the button below to start your study session."),
            Button("Begin Study", 
                   hx_get="/study",
                   hx_push_url="true",
                   hx_target="body")
        )
    )

@rt('/study')
def get_study():
    card_ids = db.get_all_card_ids()
    return Main(
            Div(id="flashcard-container", 
                style="padding-top: 30px; text-align: center;"),
            Script(f"htmx.ajax('GET', '/study/card/{card_ids[0]}', {{target:'#flashcard-container'}})")
        )

@rt('/study/card/{card_id}')
def get_next_card(card_id: int):
    card = db.get_card_by_id(card_id)
    if not card:
        return P("No more cards to study!")
    
    return Div(
        P(card['question'], style="text-align: center; font-size: 1.5em;"),
        Button("Reveal Answer", 
               hx_get=f"/study/card/{card_id}/reveal",
               hx_target="#flashcard-container"),
        style="text-align: center;"
    )

@rt('/study/card/{card_id}/reveal')
def get_reveal_answer(card_id: int):
    card = db.get_card_by_id(card_id)
    if not card:
        return P("Card not found!")
    
    all_card_ids = db.get_all_card_ids()
    next_card_id = next((id for id in all_card_ids if id > card_id), None)
    
    return Div(
        P(card['question'], style="text-align: center; font-size: 1.5em;"),
        P(card['answer'], style="text-align: center; font-size: 1.5em;"),
        Button("Next Flashcard" if next_card_id else "Complete Session", 
               hx_get=f"/study/card/{next_card_id}" if next_card_id else "/study/complete",
               hx_target="#flashcard-container"),
        style="text-align: center;"
    )

@rt('/study/complete')
def get_study_complete():
    return Div(
        P("You've gone through all the flashcards.", style="text-align: center;"),
        A("Start New Session", href="/study", cls="btn"),
        A("Back to Home", href="/", cls="btn"),
        style="text-align: center;"
    )

serve()