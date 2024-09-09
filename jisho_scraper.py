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

def word_lookup_reading(input):
    try:
        r = Word.request(input)
    except Exception as e:
        print(f"Failed to fetch reading for '{input}': {e}")
        return '-1'

    first_reading = '0'
    # Check if the response is valid and contains the 'data' attribute
    if r and hasattr(r, 'data') and r.data:
        # Access the first item in the data list
        first_entry = r.data[0]

        # Check if 'japanese' attribute exists in the first entry
        if hasattr(first_entry, 'japanese') and first_entry.japanese:
            japanese_list = first_entry.japanese

            # Access the first Japanese entry and get the reading
            first_reading = japanese_list[0].reading
            print(first_reading)
            return first_reading
        else:
            print("'japanese' attribute not found or is empty in the response data.")
            first_reading = '-1'
            return first_reading
    else:
        print("No data found in the response.")
        return first_reading

def word_lookup_definition(input_word):
    try:
        r = Word.request(input_word)
    except Exception as e:
        print(f"Failed to fetch reading for '{input_word}': {e}")
        return '-1'

    all_definitions = []

    # Check if the response is valid and contains the 'data' attribute
    if r and hasattr(r, 'data') and r.data:
        # Access the first item in the data list
        first_entry = r.data[0]

        # Check if 'senses' attribute exists in the first entry
        if hasattr(first_entry, 'senses') and first_entry.senses:
            senses_list = first_entry.senses

            # Loop through each sense and get the english_definitions
            for sense in senses_list:
                if hasattr(sense, 'english_definitions'):
                    all_definitions.extend(sense.english_definitions)
                    all_definitions.extend('/')

            if all_definitions:
                print("All definitions:", all_definitions)
                return all_definitions
            else:
                print("No definitions found.")
                return []
        else:
            print("'senses' attribute not found or is empty in the response data.")
            return []
    else:
        print("No data found in the response.")
        return []

def process_def(input_w):
    input = word_lookup_definition(input_w)
    output = 'Empty input'
    if input:
        counter = 1
        output = f"{counter}. "

        i = 0
        for entry in input:
            if len(input) - 1 == i:
                print("end of string")

            elif entry == '/':
                counter += 1
                output += f"\n{counter}. "
            else:
                output += f'{entry}; '
            i += 1
    return output
