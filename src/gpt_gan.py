import gpt_to_speech as gpt
import asyncio

maker = gpt.Conversation("Maker")
evaluator = gpt.Conversation("Evaluator")


async def chat_completion(conversation):
    output = await gpt.chat_completion(conversation)
    return output

async def main():
    first_maker_message = \
        "You are going to design a stock-picking Python script. \
        Start by coming up with a rough outline of the script. I will give you \
        feedback on your outline. Once the outline is complete, I tell you to \
        implement the outline one step at a time. I will give you feedback on \
        each step. You can ask me questions at any time. Let's get started."
    first_evaluator_message = \
        "You are going to evaluate a stock-picking Python script. \
        I will give you a rough outline of the script. You will give me feedback \
        on the outline. Once the outline is complete to your satisfaction, you \
        will tell me to implement the outline one step at a time. You will give \
        me feedback on each step. You can ask me questions at any time. Here is \
        the outline: "
    # first_maker_message = "You are a very talented MFA student. You are going to \
    #     write a short story. Start by coming up with a rough outline of the story. \
    #     I will give you feedback on your outline. Once the outline is complete, \
    #     I tell you to write the story one step at a time. I will give you \
    #     feedback on each step. You can ask me questions at any time. For your first \
    #     output, generate just the outline of the story and nothing else."
        
    # first_evaluator_message = "You are Ernest Hemingway. You are going to evaluate a \
    #     short story. I will give you a rough outline of the story. You will give me \
    #     feedback on the outline. Once the outline is complete to your satisfaction, \
    #     you will tell me to write the story one step at a time. You will give me \
    #     feedback on each step. You never ask questions, you only give feedback. \
    #     You also NEVER EVER EVER write the story yourself."
        
    evaluator.add_message(role="user", content=first_evaluator_message)
    print("Maker: ")
    maker.add_message(role="user", content=first_maker_message)
    maker_output = await chat_completion(maker)
    print("\n")
    evaluator_output = ""
    
    while True:
        print("Evaluator: ")
        evaluator.add_message(role="user", content=maker_output)
        evaluator_output = await chat_completion(evaluator)
        print("\n")
        
        print("Maker: ")
        maker.add_message(role="user", content=evaluator_output)
        maker_output = await chat_completion(maker)
        print("\n")
        

        
if __name__ == "__main__":
    asyncio.run(main())