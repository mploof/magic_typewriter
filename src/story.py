import json
import os
import random
from enum import IntEnum

import gpt_synchonous as gpt
from authors import Author
from settings import config
import bias
import images
    
class StoryPoint(IntEnum):
    CLEAR = 0
    IMAGE_NOTES = 1
    THEMES = 2
    STORY_ARC = 3
    MOTIVATIONS = 4
    START_MIDDLE_END = 5
    INTRO_IDEA = 6
    STORY = 7
    FIRST_REFINEMENT = 8
    SECOND_REFINEMENT = 9
    FINAL_REFINEMENT = 10

class Temperatures:
    IMAGE_NOTES = 0.8
    MOTIVATIONS = 1.2
    SME = 1.0
    INTRO_IDEA = 1.3
    STORY = 1.1
    FIRST_REFINEMENT = 1.0
    SECOND_REFINEMENT = 0.5
    FINAL_REFINEMENT = 0.05
    


class Story:
    
    @classmethod
    def create_empty_story(cls, story_name):
        Story(story_name, None, None, no_load=True)

    def __init__(self, story_name, author_name, image_name=None, image_url=None, image_notes=None, no_load=False):
        self.image_name = image_name
        self.image_url = image_url
        self.story_name = story_name
        self.author_name = author_name
        self.author = None
        self.story_arc = None
        self.motivations = None
        self.s_m_e = None
        self.intro_idea = None
        self.story = None
        self.story_themes = []
        self.first_refinement = None
        self.second_refinement = None
        self.final_refinement = None
        self.image_notes = image_notes
        self.messages = [
                {"role": "system", "content": f"You are a chatbot that assists with the writing of stories in the style of {self.author_name}. You have vision processing capabilities and can also process images. Your output will be processed programmatically, so please follow the instructions carefully and do not add additional commentary to your responses."}
        ]
        
        self.story_path = os.path.join(config["stories_dir"], f"{self.story_name}.json")
        
        if not no_load:
            self.load_json()
        
            # This attribute is not saved to the JSON file, so it needs to be reinitialized
            self.author = Author(author_name)
        
    def get_image_notes(self):
        if self.image_notes is None:
            print(f"Generating image notes for {self.story_name}.")
            prompt = f"Analyze the attached image and list as bullet points the following information about the subject: gender, age (guess a specific age), clothing details, body language, ethnic origin, facial expression, facial details (including, among other details, eye color and facial feature shape), hairstyle."
            content = [{"type": "text", "text": prompt}]
            
            if self.image_name is not None:
                image_url = images.get_base64_image_url(self.image_name)
                content.append({"type": "image_url", "image_url": {"url": image_url}})
            elif self.image_url is not None:
                content.append({"type": "image_url", "image_url": {"url": self.image_url}})
            else:
                print("An image name or URL must be provided to generate image notes.")
                exit()
                
            self.messages.append({"role": "user", "content": content})
            response = gpt.get_synchonous_response(messages=self.messages, temperature=Temperatures.IMAGE_NOTES)
            self.image_notes = response
            
            self.messages.append({"role": "assistant", "content": f"Image notes: {self.image_notes}"})
            
        self.save()
        return self.image_notes
    
    def fetch_story_arcs(self):
        with open(os.path.join(config["data_dir"], "story_arcs.json"), "r") as file:
            arcs = json.load(file)
            return arcs
    
    def get_character_motivations(self):
        
        if self.story_arc is None:    
            arcs = self.fetch_story_arcs()
            self.story_arc = random.sample(arcs.keys(), 1)[0]
            self.save()
        
        if self.motivations is None:
            print(f"Generating character motivations for {self.story_name}.")
            
            if self.story_themes == []:
                self.story_themes = random.sample(self.author.themes, 2)
                
            self.messages.append({"role": "user", "content": f"The story will use the following of the 8 story arcs defined by Kurt Vonnegut: {self.story_arc} -- {self.fetch_story_arcs()[self.story_arc]}. The story will be inspired by the themes of {', '.join(self.story_themes)}."})
            self.messages.append({"role": "assistant", "content": "I will make sure the story I generate follows that arc and those themes."})

            
            prompt = f"Generate motivations for the main character that fit the age, gender, ethnicity, and general demeanor of the character described in the image notes from earlier. Their motivations should fit the story arc and themes defined above. The motivations should be novel, clever, and unconventional, and should not be vague. Motivations should never be in spite of the character's age, but because of it. Mention the character's age in the motivations. What does the character want? Why? What is the character willing to do to get it? What is the character willing to sacrifice? There needs to be an impetus for the character to act, and the motivations should be clear and compelling."
            
            self.messages.append({"role": "user", "content": prompt})
            
            response = gpt.get_synchonous_response(messages=self.messages, temperature=Temperatures.MOTIVATIONS, logit_bias=bias.get_bias())
            self.motivations = response
            self.messages.append({"role": "assistant", "content": f"Character motivations: {self.motivations}"})

            self.save()
        return self.motivations
    
    def get_start_middle_end(self):
        
        if self.s_m_e is None:
            print(f"Generating start / middle / end for {self.story_name}.")
            
            if self.story_themes == []:
                self.story_themes = random.sample(self.author.themes, 2)
            
            prompt = f"Given the character motivations and story arc I also gave told you, write a brief outline of a story that includes a captivating start, a compelling middle, and a complex ending. The outline should be descriptive and matter of fact. It should not be flowery, as it is simply describing what will happen in the story. The story should be inspired by the themes of {', '.join(self.story_themes)}. List the start, middle, and end as separate bullet points. Although the story is short, there should be a clear three act structure that follows the story arc. I gave you."
            
            self.messages.append({"role": "user", "content": prompt})
          
            response = gpt.get_synchonous_response(messages=self.messages, temperature=Temperatures.SME, logit_bias=bias.get_bias())
            self.s_m_e = response
            self.messages.append({"role": "assistant", "content": f"Story Outline: {self.s_m_e}"})
          
            self.save()
        return self.s_m_e
    
    def get_intro_idea(self):
        
        with open(os.path.join(config["data_dir"], "rhetorical_devices.json"), "r") as file:
            rhethorical_devices = json.load(file)
            
        if self.intro_idea is None:
            print(f"Generating introduction ideas for {self.story_name}.")
            literary_devices = ", ".join(random.sample(self.author.devices, 2))
            prompt = f"Given the story outline and character motivations from earlier, generate a unique and captivating rhetorical idea for the introduction of the story, inspired by the following literary devices: {literary_devices}. The idea should be thought-provoking, engaging, and set the stage for a compelling narrative that follows the given plot arc. The idea should be fresh and original. Character motivations: {self.get_character_motivations()}. Plot outline: {self.s_m_e}. Some examples of interesting rhetorical ideas include: {random.shuffle(rhethorical_devices)}"

            self.messages.append({"role": "user", "content": prompt})

            response = gpt.get_synchonous_response(messages=self.messages, temperature=Temperatures.INTRO_IDEA, logit_bias=bias.get_bias())
            self.intro_idea = response
            self.messages.append({"role": "assistant", "content": f"Introduction Idea: {self.intro_idea}"})
            self.save()
        return self.intro_idea
    
    def get_story(self):
        if self.story is None:
            print(f"Generating story for {self.story_name}.")
            this_vocab = ', '.join(random.sample(self.author.get_vocab(), 50))
            prompt = f"You now know the character description, motivations, story themes, story arc, story outline, and have an idea for an interesting way to begin the story. Using that information from earlier, write the a 500 word story that follows those guidelines. Be sure to ues the story outline and introduction idea, but do not repeat them verbatim. Make sure that each paragraph in the story moves the action forward. Avoid use of the passive voice. Focus more on actions of the main character than descriptions of main character. Incorporate at at least one, but no more than two oblique references to the character's physical appears as described in the image notes. To further refine the story, incorporate some of the following vocabulary words for extra flair: {this_vocab}. These are complex words that should be used sparingly to enhance the story, not detract from it."
            
            self.messages.append({"role": "user", "content": prompt})
            
            response = gpt.get_synchonous_response(messages=self.messages, temperature=Temperatures.STORY, logit_bias=bias.get_bias())
            self.story = response
            self.messages.append({"role": "assistant", "content": f"Story first draft: {self.story}"})
            self.save()
        return self.story
    
    def get_first_refinement(self):
        if self.first_refinement is None:
            print(f"Generating first refinement for {self.story_name}.")
            this_vocab = ', '.join(random.sample(self.author.get_vocab(), 50))
            prompt = f"You will now edit the first draft of the story. Take on the roll of an editor at The New Yorker, ensuring that the story meets the highest standards for excellents in literature. Streamline the writing, cut excessive adjectives, reword awkward turns of phrase. There is no need to maintain the existing structure if you think you can restructuring and rewriting it will improve the quality and better align with {self.author.name}'s style, vocabulary, and sentence structure, so long as you maintain the character's motivations, plot arc, and story outline. Some vocabulary words to consider incorporating are: {this_vocab}. Do not use the vocabulary words excessively, but do use them when they will enhance the story. Do not remove them where they already exist. Do not reference these instructions in the story."

            self.messages.append({"role": "user", "content": prompt}),
                                 
            response = gpt.get_synchonous_response(messages=self.messages, temperature=Temperatures.FIRST_REFINEMENT, logit_bias=bias.get_bias())
            self.first_refinement = response
            self.messages.append({"role": "assistant", "content": f"First Refinement: {self.first_refinement}"})
            self.save()
        return self.first_refinement
    
    def get_second_refinement(self):
        if self.second_refinement is None:
            print(f"Generating second refinement for {self.story_name}.")
            prompt = f"This is your second edit of the story draft. In this revision, focus on removing redundancy and cliches, and condense or rephrase repetitive sections. Do not reference these instructions in the story."
            
            self.messages.append({"role": "user", "content": prompt})
            
            response = gpt.get_synchonous_response(messages=self.messages, temperature=Temperatures.SECOND_REFINEMENT, logit_bias=bias.get_bias())
            self.second_refinement = response
            self.save()
            
        return self.second_refinement
    
    def get_final_refinement(self):
        if self.final_refinement is None:
            print(f"Generating final refinement for {self.story_name}.")
            prompt = f"This is your final opportunity to enhance this story, which is already written in the style of {self.author_name}. Maintain the style, but go over it with a fine toothed comb one more time to find any hints that indicate the story might have been written by an AI and rephrase them to sound more human and less cliche. Reword any repetative word usages. Look for instances of the following cliched words and phrases and reword them in a way that is more in line with how {self.author_name} would say it: {', '.join(bias.banned_words)}. Do not reference these instructions in the story. "
   
            self.messages.append({"role": "user", "content": prompt})
            
            response = gpt.get_synchonous_response(messages=self.messages, temperature=Temperatures.FINAL_REFINEMENT, logit_bias=bias.get_bias())
            self.final_refinement = response
            self.messages.append({"role": "assistant", "content": f"Final Refinement: {self.final_refinement}"})
            self.save()
            
        print(f"Final refinement: {self.final_refinement}\n")
        return self.final_refinement
            
    def save(self):
        # Create a copy of the object's dictionary
        data_to_save = self.__dict__.copy()
        
        # List of attributes to exclude from being saved
        exclude_keys = ['author', 'author_file_path', 'story_path', 'messages']
        
        # Remove the keys you don't want to save
        for key in exclude_keys:
            data_to_save.pop(key, None)  # Use pop to remove the key, does nothing if key doesn't exist

        # Save the remaining data to a JSON file
        with open(self.story_path, "w") as file:
            json.dump(data_to_save, file, indent=4, sort_keys=True)
            
        ### Save the text of the story to a text file
        text_path = os.path.join(config["stories_dir"], f"{self.story_name}.txt")
        with open(text_path, "w", encoding="utf-8") as file:
            file.write(f"Image Notes:\n{self.image_notes}\n\n")
            file.write(f"Themes:\n{', '.join(self.story_themes)}\n\n")
            file.write(f"Story Arc:\n{self.story_arc}\n\n")
            file.write(f"Character Motivations:\n{self.motivations}\n\n")
            file.write(f"Start / Middle / End:\n{self.s_m_e}\n\n")
            file.write(f"Introduction Idea:\n{self.intro_idea}\n\n")
            file.write(f"Story:\n{self.story}\n\n")
            file.write(f"First Refinement:\n{self.first_refinement}\n\n")
            file.write(f"Second Refinement:\n{self.second_refinement}\n\n")
            file.write(f"Final Refinement:\n{self.final_refinement}\n\n")
            
    def load_json(self):
        if os.path.exists(self.story_path):
            print(f"Loading {self.story_name} from JSON.")
            with open(self.story_path, "r") as file:
                data = json.load(file)
                self.__dict__.update(data)
                
    def reset_to(self, story_point:StoryPoint):
        if story_point == StoryPoint.CLEAR:
            self.image_notes = None
        if story_point <= StoryPoint.IMAGE_NOTES:
            self.story_themes = []
        if story_point <= StoryPoint.THEMES:
            self.story_arc = None
        if story_point <= StoryPoint.STORY_ARC:
            self.motivations = None
        if story_point <= StoryPoint.MOTIVATIONS:
            self.s_m_e = None
        if story_point <= StoryPoint.START_MIDDLE_END:
            self.intro_idea = None
        if story_point <= StoryPoint.INTRO_IDEA:
            self.story = None
        if story_point <= StoryPoint.STORY:
            self.first_refinement = None
        if story_point <= StoryPoint.FIRST_REFINEMENT:
            self.second_refinement = None
        if story_point <= StoryPoint.SECOND_REFINEMENT:
            self.final_refinement = None
        self.save()
        
    
if __name__ == "__main__":
            
    story = Story("Michael Story New", "D.H. Lawrence", image_name="michael.jpg")
    story.reset_to(StoryPoint.CLEAR)
    story.get_image_notes()
    story.get_character_motivations()
    story.get_start_middle_end()
    story.get_intro_idea()
    story.get_story()
    story.get_first_refinement()
    story.get_second_refinement()
    story.get_final_refinement()
