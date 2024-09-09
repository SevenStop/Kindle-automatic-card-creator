from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import *
import re
from .jisho_scraper import *
from .pitch_dict_functions import *
import sys
import os

# Determine the path to the bundled pydantic and jisho-api packages
addon_path = os.path.dirname(__file__)
pydantic_path = os.path.join(addon_path, 'pydantic_bundle')

# Add the path to sys.path
sys.path.insert(0, pydantic_path)

# Now you can import pydantic and jisho-api
from pydantic import BaseModel
from jisho_api.word import Word

def addCard(sentence, audio, back_word_pitch, back_word, reading, definition, note_type = 'JPB'):
    col = mw.col

    model = col.models.by_name(note_type)

    if not model:
        showInfo(f"Note type {note_type} not found")
        return

    note = col.new_note(model)
    if sentence:
        note.fields[0] = sentence
    if audio:
        note.fields[1] = audio
    if back_word_pitch:
        note.fields[2] = back_word_pitch
    if back_word:
        note.fields[3] = back_word
    if reading:
        note.fields[4] = reading
    if definition:
        note.fields[5] = definition

    # Get the deck ID
    deck_name ='文'
    deck_id = get_deck_id(deck_name)
    if not deck_id:
        return 0  # Failure

    note.note_type()['did'] = deck_id

    if col.add_note(note, deck_id):
        #1 means success
        return 1
    else:
        #0 means fail
        return 0

def input_path():
    path1, ok = QInputDialog.getText(mw, "Path of sentence file", "Enter the path for the sentence file:")
    if not ok or not path1.strip():
        showInfo("Invalid")
        return

    path2, ok = QInputDialog.getText(mw, "Path of word file", "Enter the path for word file:")
    if not ok or not path2.strip():
        showInfo("Invalid")
        return

    #regex detects the texts between ": " and "("
    pattern = r'(?<=: ).*?(?=\()'
    sentences = []

    #hardcode for testing
    #path1 = "C:\\Users\\comma\\Documents\\プログラミング\\output.txt"
    #path2 = "C:\\Users\\comma\\Documents\\プログラミング\\words.txt"

    #read the sentence file
    try:
        with open(path1, 'r', encoding='utf-8') as file:
            for line in file:
                match = re.search(pattern, line)
                if match:
                    sentences.append(match.group())
    except FileNotFoundError:
        showInfo(f"File {path1} not found")
        return
    except Exception as e:
        showInfo(f"An error occurred while reading the file: {e}")
        return

    print(sentences)

    words = []

    #read the word file
    try:
        with open(path2, 'r') as file:
            words = file.readlines()

        # Strip newline characters from each line
        words = [line.strip() for line in words]

    except FileNotFoundError:
        showInfo(f"File {path2} not found")
        return
    except Exception as e:
        showInfo(f"An error occurred while reading the file: {e}")
        return

    print(words)

    #load pitch dict
    filename = 'C:\\Users\\comma\\AppData\\Roaming\\Anki2\\addons21\\kindlecards\\accents.txt'
    word_dict = load_data(filename)

    #output for search failures
    nfoutput = []

    #test counter to limit the number of times the loop runs
    tc = 0
    #iterate through words with current
    for current in words:
        found = True
        snf, anf, bwpnf, bwnf, rnf, dnf = False, False, False, False, False, False

        #if tc == 10:
        #    break;

        #process the line
        print(current)
        #if there is a conjugation the lookup is after the colon
        #search is for getting the sentence and lookup for jisho

        #cstate indicates whether multiple words, conjugations, or normal. 0 is normal. Conjugation is 1 and multi is 2
        search = ''
        search2 = None
        lookup = current
        lookup2 = ""
        cstate = 0

        if ';' in current:
            conjugation_parts = current.split(';')
            search = conjugation_parts[0]
            lookup = conjugation_parts[1]
            current_sent = [item for item in sentences if search in item]
            cstate = 1

        #if there are two words do two lookups
        elif ":" in current:
            mult_words = current.split(':')
            search = mult_words[0]
            lookup = search
            search2 = mult_words[1]
            lookup2 = search2
            cstate = 2

            current_sent = [item for item in sentences if search in item]

        else:
            #sentence always equals current
            current_sent = [item for item in sentences if current in item]
            search = current


        if current_sent:
            sentence = current_sent[0]
        else:
            sentence = 'Sentence not found'
            snf = True
            found = False

        #audio lookup forvo
        audio = ''

        #pitch lookup??
        back_word_pitch = '1'
        if cstate == 0 or cstate == 1:
            back_word_pitch = lookup_word(word_dict, lookup)
            back_word_pitch = back_word_pitch[0]
        else:
            back_word_pitch = lookup_word(word_dict, lookup)
            back_word_pitch += '; ' + lookup_word(word_dict, lookup2)[0]

        #word insert
        back_word = '1'
        if cstate == 0:
            back_word = current

        elif cstate == 1:
            back_word = lookup
        else:
            back_word = f'{lookup}; {lookup2}'

        #reading lookup
        reading = '1'
        if cstate == 1 or cstate == 0:
            reading = word_lookup_reading(lookup)
        else:
            reading = f'{word_lookup_reading(lookup)} ;\n{word_lookup_reading(lookup2)}'

        #definition lookup
        definition = '1'
        if cstate == 1 or cstate == 0:
            definition = process_def(lookup)
        else:
            definition = f'{process_def(lookup)} ;\n{process_def(lookup2)}'

        if not found:
            nfoutput.append(f'Sentence: {snf}; Audio: {anf}; Back Word Pitch: {bwpnf}; Back Word: {bwnf}; Reading: {rnf}; Definition: {dnf}')

        print(search, search2)
        if sentence:
            sentence = sentence.replace(search,f'<span style="color:#00aa00">{search}</span>')
            if search2:
                sentence = sentence.replace(search2, f'<span style="color:#00aa00">{search2}</span>')

        if definition:
            definition = definition.replace('\n', '<br>')

        print(sentence, audio, back_word_pitch, back_word, reading, definition)
        state = addCard(sentence, audio, back_word_pitch, back_word, reading, definition)
        print(state)
        tc += 1

    with open('output.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(nfoutput))

def get_deck_id(deck_name):
    col = mw.col
    deck = col.decks.by_name(deck_name)
    if deck:
        return deck['id']
    else:
        showInfo(f"Deck {deck_name} not found")
        return None

# Create a new menu item for adding a card
action = QAction("Add Cards", mw)
qconnect(action.triggered, input_path)
mw.form.menuTools.addAction(action)

# Optionally, bind the action to a keyboard shortcut
shortcut = QShortcut(QKeySequence("Ctrl+Shift+K"), mw)
qconnect(shortcut.activated, input_path)