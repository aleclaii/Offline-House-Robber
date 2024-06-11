import pygame, sys, random
import requests
import json

class Game:
    def __init__(self):
        self.stage = 0
        self.difficulty = random.choice(['Baby'])#, 'Easy' , 'Medium', 'Intermediate', 'Hard', 'Realistic'])
        self.scenario_text = random.choice([
            "You see a house with an open window. What do you do?",
            "You spot a bank and there isn't anyone else around. What do you do?",
            "You come across a mansion in the woods. What do you do?",
            "You find a yacht docked at the pier with no one around. What do you do?",
            "You see a jewelry store with minimal security. What do you do?",
            "You discover an art gallery with rare paintings. What do you do?",
            "You come across a high-security compound. What do you do?",
            "You find a huge mansion in a gated community. What do you do?",
            "You notice an antique shop with valuable items. What do you do?",
            "You come across a tech company’s headquarters. What do you do?",
            "You wash up onto a billionaire's private island. What do you do?",
            "You come across an auction house with rare items up for bid. What do you do?",
            "You see a secret government high-tech lab. What do you do?",
            "You come across a posh casino with loose security. What do you do?",
            "You find a historical library with rare books. What do you do?"
        ])
        self.loot = random.choice([
            "Antique vase",
            "Pink Diamond",
            "Gold Bars",
            "Rare Paintings",
            "Bearer Bonds",
            "Faberge Egg",
            "Vintage coins",
            "Confidential USB",
            "Unmarked Weapons",
            "Vintage Watches",
            "Incriminating Evidence",
            "Bank Notes",
            "Secret Vault Codes",
            "Meteorite",
            "Unicorn Horn"
        ])
        self.preperation_text = "You plan on stealing something tonight, what will you bring?"
        self.gameover = False
        self.input_text = ''
        pygame.init()
        self.screen = pygame.display.set_mode((1600, 800))
        pygame.display.set_caption("House Robber Simulator")
        self.font = pygame.font.Font(None, 24)

    def determine_outcome(self):
        match self.difficulty:
            case 'Baby':
                outcome = random.choices(('Negative', 'Positive'), k=1, weights=(0, 100))
            case 'Easy':
                outcome = random.choices(('Negative', 'Positive'), k=1, weights=(5, 150))
            case 'Medium':
                outcome = random.choices(('Negative', 'Positive'), k=1, weights=(10, 120))
            case 'Intermediate':
                outcome = random.choices(('Negative', 'Positive'), k=1, weights=(20, 140))
            case 'Hard':
                outcome = random.choices(('Negative', 'Positive'), k=1, weights=(30, 180))
            case 'Realistic':
                outcome = random.choices(('Negative', 'Positive'), k=1, weights=(40, 100))
        return outcome[0]

    def request_ai(self, request_type: str, scenario: str = "", action: str = "", items: list[str] = [], result: str = '') -> str:
        system_message = ""
        user_message = ""
        if request_type == "inventory":
            system_message = f"You are a game master. Your job is to determine which items are suitable for a heist based on the difficulty level {self.difficulty}."
            user_message = f"Given the following list of items: {', '.join(items)}, determine which items can and cannot be brought on a heist. For Baby mode, allow the player to bring anything, even illogical items or people. In Easy mode, allow anything. In Medium mode, limit items. In Hard mode, only allow items realistically available to a middle-class citizen. Return the list in the format: item (Available/Unavailable), DO NOT say anything else other than the list itself."
        
        elif request_type == "scenario":
            if result == 'Positive':
                user_message = f"Generate a new scenario based on the previous scene: {scenario}, the previous action: {action}, and the current stage of the robbery {self.stage}. The player currently has: {items}. If the previous action was unrelated, mention that. If {self.stage} equals 6, generate a game-winning text explaining how the player escaped with the {self.loot}. Format the response as follows:\n\nStage: ({self.stage})\nInventory: ({', '.join(items)})\nResponse: "
            else:
                system_message = f"You are a game master. Create a gameover message based on the previous scenes and actions. The player is a thief, and the robbery has 6 stages: 0 - preparation, 1 - infiltration, 2-4 - dealing with complications, 5 - stealing the item, 6 - exfiltration. The current loot target is {self.loot}, and the current stage is {self.stage}."
                user_message = f"Generate a gameover text based on the previous scene: {scenario}, the previous action: {action}, and the current stage: {self.stage}. The player currently has: {items}. If the previous action was unrelated, mention that. Explain how the player was caught and lost the game, without including 'Game Over'. Format the response as follows:\n\nStage: ({self.stage})\nInventory: ({', '.join(items)})\nResponse: "

        # Prepare data for Dolphin Llama request
        prompt = f"{system_message}\n\n{user_message}"
        url = "http://localhost:11434/api/generate"
        headers = {'Content-Type': 'application/json'}
        data = {
            "model": "llama3", #dolphin-llama3
            "stream": False,
            "prompt": prompt
        }

        # Make request to Dolphin Llama API
        response = requests.post(url, headers = headers, data = json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            actual_response = response_data["response"]
            return actual_response
        else:
            print("Error:", response.status_code, response.text)
            return "Error: Could not generate response."

    def wrap_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''

        for word in words:
            test_line = current_line + word + ' '
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + ' '

        lines.append(current_line.strip())
        return lines

    def display_text(self, text, y):
        max_width = self.screen.get_width() - 40
        lines = self.wrap_text(text, max_width)
        for i, line in enumerate(lines):
            render = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(render, (20, y + i * 40))

    def main(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if not self.gameover:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if self.stage == 0:
                                self.items = self.input_text.split(',')
                                self.items = [item.strip() for item in self.items]
                                self.input_text = ''
                                validated_items = self.request_ai('inventory', items=self.items)
                                self.scenario_text = "Available Items: " + "".join(validated_items) + ". " + self.scenario_text
                                self.stage += 1
                            else:
                                action = self.input_text
                                self.input_text = ''
                                outcome = self.determine_outcome()
                                new_scenario = self.request_ai("scenario", scenario=self.scenario_text, action=action, items=self.items, result=outcome)
                                self.stage += 1
                                if outcome == 'Positive':
                                    if self.stage == 6:
                                        self.scenario_text = new_scenario
                                        self.gameover = True
                                    else:
                                        self.scenario_text = new_scenario
                                else:
                                    gameover_message = self.request_ai("scenario", scenario=self.scenario_text, action=action, items=self.items, result=outcome)
                                    self.scenario_text = f"{gameover_message} Game Over"
                                    self.gameover = True
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            self.input_text += event.unicode

            self.screen.fill((0, 0, 0))
            if self.stage == 0:
                self.display_text(self.preperation_text, 20)
            else:
                self.display_text(self.scenario_text, 20)
            self.display_text("Your action: " + self.input_text, 500)
            self.display_text("Target: " + self.loot, 710)
            self.display_text("Stage: " + str(self.stage), 740)
            self.display_text("Difficulty: " + str(self.difficulty), 770)
            pygame.display.flip()
            clock.tick(30)

if __name__ == "__main__":
    game = Game()
    game.main()
