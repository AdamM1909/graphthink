
# add a few boxes like select tag, then give a drop down of all questions to pick from. 

from backend.db import *
from fasthtml.common import *

app, rt = fast_app()

decks = ['ch1', 'ch2', 'ch3']
questions = {
    'ch1': ['lesson1', 'lesson2', 'lesson3'],
    'ch2': ['lesson4', 'lesson5', 'lesson6'],
    'ch3': ['lesson7', 'lesson8', 'lesson9']
}

def make_dropdown(name, options): return (Option(f'-- select {name} --', disabled='', selected='', value=''), *map(Option, options))
def make_node_selection_column(to_from):  
    deck_dropdown = Select(*make_dropdown('deck', decks), name='deck', hx_get='/questions', hx_target=f'#questions_{to_from}')
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
def questions_in_deck(deck: str): return make_dropdown('flashcard', questions[deck])
    
serve()