# Function to load the data from the file into a dictionary
def load_data(filename):
    word_dict = {}

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('\t')  # Split line by tab character

            if len(parts) == 3:  # Check if the line has exactly 3 parts
                word = parts[0]  # First column: the word (e.g., '１', '１０００円')
                pronunciation = parts[1]  # Second column: pronunciation (e.g., 'いち', 'せんえん')
                numbers = parts[2].split(',')  # Third column: split numbers by comma (e.g., '2', '0')

                word_dict[word] = numbers  # Store the numbers in the dictionary

    return word_dict


# Function to look up a word in the dictionary and return the corresponding numbers
def lookup_word(word_dict, word):
    return word_dict.get(word, "X")