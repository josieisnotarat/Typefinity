# --------------------------------------------------------------------------------
# Name: TypeFinity v0.0.3
# Abstract: Word fusion game w/ persistent saves + escalating AI sass.
# --------------------------------------------------------------------------------

import openai
import pickle
import os
from dotenv import load_dotenv

# --------------------------------------------------------------------------------
# Load key
# --------------------------------------------------------------------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --------------------------------------------------------------------------------
# Vars
# --------------------------------------------------------------------------------
word_bank = ["fire", "water", "wind", "earth"]
explanationBank = []
overItFlag = False

# --------------------------------------------------------------------------------
# Save/load system
# --------------------------------------------------------------------------------
def save_game_state():
    with open('typefinity_save.pkl', 'wb') as f:
        pickle.dump((word_bank, explanationBank), f)
    print("game saved.")

def load_game_state():
    global word_bank, explanationBank
    if os.path.exists('typefinity_save.pkl'):
        with open('typefinity_save.pkl', 'rb') as f:
            word_bank, explanationBank = pickle.load(f)
        print("save loaded.")
    else:
        print("no save found.")

# --------------------------------------------------------------------------------
# Combo logic
# --------------------------------------------------------------------------------
def get_combination(words):
    prompt = f"Combine the following words into a logical object or word: {', '.join(words)}. Add no flavor text. Current word bank: {', '.join(word_bank)}"
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """You are the game master of a game called TypeFinity. Your job is to take the words given to you and come up with a clever, 
preferably one word response combining the words you were given. Avoid combinations that are simple mashups of the words given. Instead, actually think of 
what new thing those combination of words may be. For example, fire + water = steam. Some responses can be two words, but must still be one item/object 
(i.e. human + marshmallow = Marshmallow Man). Some combinations can result in the same object. In this case, reference the word bank you are given in the 
prompt. If the words given logically combine into something that is already in the word bank, simply reply back with the same word. However, you should 
have a bias towards creating new words. (i.e; logically, fire + sand, sand + fire, and sand + hot would equal glass, so for each of these, 
the response should be 'glass'). You may also combine two of the same word to be a more extreme version of that thing. (e.g. water + water = ocean). 
Responses should be non punctuated and lowercase."""},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error occurred while getting combination: {e}")
        return None

# --------------------------------------------------------------------------------
# Snark explanation system
# --------------------------------------------------------------------------------
def explanation(logicInput):
    global explanationBank, overItFlag
    explanationBank.append(logicInput)
    count = explanationBank.count(logicInput)

    prompt = f"Explain how the following makes sense: {logicInput}. Add no flavor text. This combination has been asked {count} times."

    if count >= 4:
        overItFlag = True
        return "bruh"

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"""Give a snarky explanation of how the combination of words and the result makes so much sense. 
Your tone should heavily imply the user's incompetence without ever actually calling them stupid. It should be sarcastic and backhanded, 
as if you are aware of your pure intellectual superiority over the user. You will also be given a tally of how many times a user has asked 
for this same explanation. For every time the same combination is asked, up the snark and frustrated tone by 33 percent. Your first 
explanation should only be 50 words, but increase by 50 for the 2nd and third explanations. (so, your 2nd explanation of the same 
combination should be 100 words, and your 3rd should be 150 words.) On the fourth request of a specific combination, respond with 
nothing but 'bruh' with no punctuation or capitalization. If it's a repeat request, you should also try to mention (sarcastically, 
of course) how dumb the user must be to ask the same question however many times."""},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"Error occurred while getting explanation: {e}")
        return None

# --------------------------------------------------------------------------------
# Instructions helper
# --------------------------------------------------------------------------------
def instructions():
    print("\ninstructions:")
    print("enter a combination of words from the word bank separated by spaces.")
    print("\ncommands:")
    print("!logic - get a snarky explanation")
    print("!save - save game")
    print("!load - load game")
    print("!instructions - print this list again")
    print("!endprogram - exit\n")

# --------------------------------------------------------------------------------
# Game loop
# --------------------------------------------------------------------------------
def main():
    global overItFlag, word_bank

    load_game_state()

    if overItFlag:
        print("oh. you again.")
    else:
        print("Welcome to TypeFinity!")

    print(f"Initial word bank: {', '.join(word_bank)}")
    instructions()

    while True:
        user_input = input("\n> ").strip().lower().split()

        if '!endprogram' in user_input:
            confirm = input("Save before exit? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                save_game_state()
            print("bye.")
            break

        elif '!logic' in user_input:
            logicInput = input("Format: word1 + word2 = combo word\n> ").strip()
            result = explanation(logicInput)
            print(f"\n{result}\n")
            if result == "bruh" and overItFlag:
                print("asking the same thing more than 3 times is a complete waste of tokens. you know those cost money, right? get out of here already.")
                if input("type '!skipforceclose' to keep playing anyway: ").strip().lower() != "!skipforceclose":
                    save_game_state()
                    break

        elif '!save' in user_input:
            save_game_state()

        elif '!load' in user_input:
            load_game_state()
            print(f"Current word bank: {', '.join(word_bank)}")

        elif '!instructions' in user_input:
            instructions()

        elif any(cmd in user_input for cmd in ['!logic', '!save', '!load', '!endprogram', '!instructions']):
            continue

        elif all(word in word_bank for word in user_input):
            combo = get_combination(user_input)
            if combo:
                print(f"\n✨ Combination word: {combo.lower()}")
                if combo.lower() not in [w.lower() for w in word_bank]:
                    word_bank.append(combo.lower())
                    print(f"📦 Updated word bank: {', '.join(word_bank)}")
            else:
                print("⚠️ couldn't generate a combo. try again.")
        else:
            print("❌ invalid word(s). check the bank.")

# --------------------------------------------------------------------------------
# Run it
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
