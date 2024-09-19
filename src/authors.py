import gpt_synchonous as gpt
import json
import yaml
import os
import random

from settings import config

authors_list = ['William Shakespeare', 'Jane Austen', 'Mark Twain', 'Charles Dickens', 'Arthur Conan Doyle', 'H.P. Lovecraft', 'Ernest Hemingway', 'George Orwell', 'Leo Tolstoy', 'Emily Dickinson', 'Edgar Allan Poe', 'Fyodor Dostoevsky', 'Virginia Woolf', 'James Joyce', 'Haruki Murakami', 'J.K. Rowling', 'J.R.R. Tolkien', 'Gabriel García Márquez', 'Toni Morrison', 'Langston Hughes', 'Sylvia Plath', 'Herman Melville', 'Mary Shelley', 'Franz Kafka', 'Agatha Christie', 'Oscar Wilde', 'Charles Baudelaire', 'Italo Calvino', 'Margaret Atwood', 'Chinua Achebe', 'Zora Neale Hurston', 'Kurt Vonnegut', 'Ray Bradbury', 'George R.R. Martin', 'Alice Walker', 'Kazuo Ishiguro', 'Philip K. Dick', 'Toni Cade Bambara', 'Isabel Allende', 'T.S. Eliot', 'Louisa May Alcott', 'Dante Alighieri', 'Nikolai Gogol', 'Anton Chekhov', 'W.B. Yeats', 'Henry James', 'Octavia E. Butler', 'Samuel Beckett', 'Gustave Flaubert', 'James Baldwin', 'John Steinbeck', 'Maya Angelou', 'F. Scott Fitzgerald', 'Hermann Hesse', 'Jorge Luis Borges', 'Salman Rushdie', 'Ursula K. Le Guin', 'David Foster Wallace', 'Elena Ferrante', 'Yukio Mishima', 'Cormac McCarthy', 'Rumi', 'J.D. Salinger', 'Clarice Lispector', 'Françoise Sagan', 'Amos Oz', "Ngũgĩ wa Thiong'o", 'Joan Didion', 'Khaled Hosseini', 'Albert Camus', 'Anne Carson', 'Banana Yoshimoto', 'Charles Bukowski', 'Don DeLillo', 'Eudora Welty', "Flannery O'Connor", 'Günter Grass', 'Harper Lee', 'Iris Murdoch', 'Jack Kerouac', 'Kenzaburō Ōe', 'Lorrie Moore', 'Mikhail Bulgakov', 'Nawal El Saadawi', 'Octavio Paz', 'Patricia Highsmith']

class Author:
    def __init__(self, name):
        self.name = name
        self.genre = None
        self.complexity = 0
        self.poeticism = 0
        self.vocab = []
        self.themes = []
        self.devices = []
        self.writing_sample = None

        self.author_file_path = os.path.join(config["authors_dir"], f"{self.name}.json")
        self.load_author_file()        


        
    def __str__(self):
        return f"{self.name}: {self.genre}, Complexity: {self.complexity}, Poeticism: {self.poeticism}, Themes: {self.themes}, Devices: {self.devices}, Vocab: {self.vocab}"   

    def initalize_author(self):
        self.get_themes()
        self.get_devices()
        self.get_genre()
        self.get_complexity()
        self.get_poeticism()
        self.get_vocab(150)
        self.get_writing_sample()
        
    def get_vocab(self, vocab_size=150):
        '''Prompt ChatGPT to return a list of vocabulary specific to the author'''
        
        def update_vocab():
            max_words_per_request = 75
            words_to_request = vocab_size - len(self.vocab)
            if words_to_request > max_words_per_request:
                words_to_request = max_words_per_request
                
            prompt = f"Generate a list of {words_to_request} words that typify {self.name}'s writing style in the form of a space separated list. Be sure these were actual words used in thir writing and are not just descriptors of their writing. Do not include invented words in this list, only real English words. Do not include words from books or stories by the author. The list should include words spanning all complexities levels typical of the author's writing aside from basic grammatical words. Again, this will be processed directly by a script, so output nothing but the list."
            
            print(f"Target vocab size: {vocab_size}, Current vocab size: {len(self.vocab)}, Fetching {words_to_request} more words.")
            
            if len(self.vocab) > 0:
                current_vocab = " ".join(self.vocab)
                prompt += f" The current list of words for {self.name} has already been recorded: {current_vocab}. Do not repeat these words or any varients of them."
            
            response = gpt.get_synchronous_response(prompt, temperature=0.05, model="gpt-4-turbo")
            vocab = response.replace(".", "").replace(",", "").replace("\n", " ").strip().split(" ")
            for word in vocab:
                if word.lower() not in self.vocab:
                    self.vocab.append(word.lower())
            
            self.save_author_file()
                   
            # Continue to request words until the vocab list is at least the desired size
            if len(self.vocab) < vocab_size:
                update_vocab()
        
        if len(self.vocab) < vocab_size - 10:
            update_vocab()
            print("Vocab size:", len(self.vocab))
            print("Vocab:", self.vocab)
        
        random.shuffle(self.vocab)
        return self.vocab
        
    def get_themes(self):
        
        if self.themes is None or len(self.themes) == 0:
            print(f"Generating themes for {self.name}.")
            prompt = f"Generate a comma separated list of recurring themes that {self.name} is known for writing about. This will be processed directly by a script, so output nothing but the list."
            response = gpt.get_synchronous_response(prompt)
            themes = response.split(",")
            for theme in themes:
                self.themes.append(theme.lower())
            self.save_author_file()
            print("Themes:", self.themes)
        return self.themes

    def get_devices(self):
        
        if self.devices is None or len(self.devices) == 0:
            print(f"Generating literary devices for {self.name}.")
            prompt = f"Generate a comma separated list of literary devices that {self.name} is known for using in their writing. This will be processed directly by a script, so output nothing but the list."
            response = gpt.get_synchronous_response(prompt)
            devices = response.split(",")
            for device in devices:
                self.devices.append(device.lower())
            self.save_author_file()
            print("Literary devices:", self.devices)
        return self.devices
        
    def get_genre(self):
        if self.genre is None:
            print(f"Generating genre for {self.name}.")
            prompt = f"Output the genre {self.name} is most known for writing in. This will be processed directly by a script, so output nothing but the description."
            response = gpt.get_synchronous_response(prompt)
            self.genre = response.lower()
            self.save_author_file()
            print("Genre:", self.genre)
        
    def get_complexity(self):
        if self.complexity == 0:
            print(f"Generating complexity rating for {self.name}.")
            prompt = f"Output a complexity rating for {self.name}'s writing style on a scale of 1-10. This will be processed directly by a script, so output nothing but the number."
            response = gpt.get_synchronous_response(prompt)
            self.complexity = int(response)
            self.save_author_file()
            print("Complexity:", self.complexity)
        return self.complexity
        
    def get_poeticism(self):
        if self.poeticism == 0:
            prompt = f"Output a poeticism rating for {self.name}'s writing style on a scale of 1-10. This will be processed directly by a script, so output nothing but the number."
            response = gpt.get_synchronous_response(prompt)
            self.poeticism = int(response)
            self.save_author_file()
            print("Poeticism:", self.poeticism)
        return self.poeticism
    
    def get_writing_sample(self):
        if self.writing_sample is None:
            with open(os.path.join(config["authors_dir"], "writing_seed.txt"), "r") as file:
                seed_text = file.read()
            prompt = f"Re-write text this in the style of {self.name}. This will be processed directly by a script, so output nothing but the re-written text. \n\n {seed_text} "
            response = gpt.get_synchronous_response(prompt)
            self.writing_sample = response
            self.save_author_file()
            print("Writing sample:", self.writing_sample)
        return self.writing_sample  
        
    def save_author_file(self):

        # Create a copy of the object's dictionary
        data_to_save = self.__dict__.copy()
        
        # List of attributes to exclude from being saved
        exclude_keys = ['author_file_path']
        
        # Remove the keys you don't want to save
        for key in exclude_keys:
            data_to_save.pop(key, None)  # Use pop to remove the key, does nothing if key doesn't exist

        # Save the remaining data to a JSON file
        with open(self.author_file_path, "w") as file:
            json.dump(data_to_save, file, indent=4, sort_keys=True)

    def load_author_file(self):
        if os.path.exists(self.author_file_path):
            print(f"Loading {self.name} from JSON.")
            with open(self.author_file_path, "r") as file:
                data = json.load(file)
                self.__dict__.update(data)
            self.get_vocab(150)
        else:
            self.initalize_author()
            
def get_initialized_authors():
    author_files = os.listdir(config["authors_dir"])
    for file in author_files:
        with open(config["authors_dir"], "r") as f:
            data = yaml.safe_load(f)
            author = data["name"]
            print(author)


def check_for_duplicates(authors_list):
    for item in authors_list:
        name = item["name"]
        count = 0
        for this_item in authors_list:
            if this_item["name"] == name:
                count += 1
        if count > 1:
            print(f"Duplicate: {name}")


if __name__ == "__main__":
    # author = Author("David Foster Wallace", 150)
    get_initialized_authors()