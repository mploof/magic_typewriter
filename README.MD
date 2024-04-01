# Magic Typewriter

This project will consist of the following general components:
1. ChatGPT interface with the following modes:

    | Input   | Output |
    |---------|--------|
    | Text    | Text   |
    | Text    | Voice  |
    | Voice   | Text   |
    | Voice   | Voice  |

2. Multiple chat personas
3. IoT electric typewriter
    - Paper position control
    - Key actuation
    - Key input sensing
    - End-of-line bell activation

The fusion and juxtposition of AI chat assistants with analog physical I/O creates the opportunity for wide array of artistic explorations and commentary regarding the nature of technology, isolation, and connectedness in contemporary Western society. 

## Potential Projects

### AOL Instant Typewriter (a.k.a. WhatsTap)

Three similarly configured typewriters are connected to a chat server via websocket for real-time interaction. Each typewriter manages two conversations on the page, one justified left, the other justified right. When the user of one machine types a message, it is populated by the other two typewriters in the appropriate chat column. The users may press a special key to switch between chats. The forward/backward page control of the typewriters allow them to manage moving back and forth between two chats that may be on different lines of the page.

This project recontextualizes instant messaging and texting in form of a dedicated appliance, giving the user the chat equivalent using a landline phone. With no opportunity for context switching, the user is invited to give their full and undivided attention to their textual conversation.

**Possible project expansion**

Pair the dedicated connected typewriters with rotary-dial phones. The phones may be used in the following ways:
- Voice-to-text input devices. The input used to send text chat messages
- They may simply connect to the other phones once the users become frustrated with the slow pace of typing
- For users who are uncomfortable with the instantaneous nature of direct phone-calling and the sound of their own voice, their speech can be processed to text, then the text re-converted to speech with an alternate voice, which is received on the other end of the line.  


### The Digital Gaze

A webcam sits on top of the typewriter. The user presses a special key, which captures a photo of the user. The image is uploaded to ChatGPT, which then generates an opening paragraph describing the person in the image as if they were a character being introduced in a literary novel.


### The Ghost of Hemingway

After the user composes a paragraph of prose, the ghost of Ernest Hemingway harshly critiques the writing and, if he thinks it interesting enough subject matter, re-writes it in his own style.

### Collaborative Poetry Generator

When the user presses a special key, the typewriter continues with the next word of the poem, allowing the writer to selectively request compositional assistance.

### Ink, Interrupted

The user is invited to use the typewriter to write whatever they like. As they type, they are frequently interrupted by the typewriter taking over and typing out unimportant "BREAKING NEWS" alerts, "modal" pop-up windows advertising anachronistic products, or inbox notifications. The end-of-line bell frequently rings to alert the typist of background notifications.

By incorporating the types of distractions we encounter on a daily basis into the context of the normally distraction-free experience of a typewriter, the work throws into sharp relief the absurdity of the demands for attention made by modern technology meant to ease the burdens of daily life.

### Speak & Spell

Using the voice mode input, the user gives dictation, which is then transcribed by the typewriter. The AI assistant will sometimes give spoken feedback on the substance or style of the dictation, and occasionally modify the input to its liking before typing the result.

## Installation

### All platforms

Create a directory called `keys` in the project root, then place your ChatGPT and ElevenLabs API key files there. Make sure you've updated `config.yaml` to point to your key files.

### Linux

```
chmod +x setup.sh
chmod +x run.sh
sudo ./setup.sh
```

### Windows

Run PowerShell as administrator
```
./setup.ps1
```

## Execution

Currently, only the chat interface component of this project is implemented. When you execute the run script, it will open a chat interface with the given input/output modes specified in `config.yaml`. See more on chat modes below.

### Linux

```
./run.sh
```

### Windows

```
./run.ps1
```

## How to Use The Chat

### Voice Input

In voice input mode, the application will constantly listen for speech input. Each time there is a break in speech, the input is finalized. 

If `use_wake_word` is `True`, when a speech input is finalized, it will look for the first instances of a wake word, then use everything after that as the command / chat input.

If `use_wake_word` is `False`, the contents of each finalized speech will be interpreted as a command / chat input. This is not a good option to use if there is ambient background speech, or you are having conversations with people other than the chat interface. It can also be a bit finicky and capture non-speech fragments as words, leading to unintended input. This is mainly useful if you're having an uninterrupted conversation with the chat agent.

The default/override wake word is set in `config.yaml`. The override wake word will always work in all contexts, when when speaking to a particular character, you may also use their name as the wake word. See more about characters below.

Speech-to-text in this application is handled on your local machine, so no need to worry about API costs.

### Text Input

No need for a "wake word." Everything you type will be directly interpreted as a command for chat input.

### Voice Output

Streaming messages from ChatGPT are fed to the streaming voice generation API from ElevenLabs and then streamed to an audio output. The ElevenLabs API isn't particularly cheap, so you may not want to overuse it.

### Text Output

Basically just the normal text output you're used to seeing from the ChatGPT UI, but in your terminal. You can still use voice input with this mode, though.

### Commands

| Command                      | Effect                                                                                                                                                                       |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| talk to \<chat character name> | If there is no existing conversation with the specified character, a new one is started. If there is, it is resumed from where you left off when you switched to a different conversation. |
| undo                         | Removes the last pair of chatbot and user messages                                                                                                                           |
| clear                        | Resets the conversation to the chat character's initial context                                                                                                              |
| exit                         | Exits the program and cleans up background threads. This is preferred over `ctrl+C` for this reason.                                                                          |
| image: \<url to image> [rest of your message]  | This is only applicable in text input mode. This allows you to pass an image to the chat agent as part of your conversation.

### Chat Characters

When you begin a chat session, you by default are speaking to a generic AI assistant. You may use the `talk to` command to have a conversation with a particular character. The application will look for an ElevenLabs voice and a character context matching that name. If the voice is not found, the default voice will be used. If the character context is not found, the default context is used.

Your message history with each character is saved with that particular character, so when you switch away and back to a conversation, you pick up where you left off. Currently, all message histories are lost when you close the application.

To add a new character context, create a file called `<character_name>_context.txt` in the `contexts` directory.

### ChatGPT Models

Unless you need a more advanced model, it's suggested to keep the `chat_model` in `config.yaml` set to `gpt-3.5-turbo` unless otherwise needed as calls to this model are 20x cheaper than `gpt-4-turbo-preview` and 40x cheaper than `gpt-4`. See more here: https://openai.com/pricing


## Project Architecture

### Typewriter Compute Module

Depending on the specific project application, the typewriter module may be either a single board computer or microcontroller. In the case of projects that require significant local computing power--e.g. capturing photos, performing local voice-to-text capture, etc.--a single board computer (SBC) running a streamlined Linux distribution is the preferred solution. For projects with more basic I/O requirements--e.g. passing messages to and from a GPT chat API--a microcontroller (MCU) such as the ESP-32 is preferred.

This project will pursue both options:

The SBC implementation will use a Raspberry Pi running a custom Linux distribution built with Yocto to streamline the operating system's footprint, and ensure repeatability when distributing the project to other devices.

The MCU implementation will use an ESP-32 or Cortex-M series MCU running ESP-IDF or FreeRTOS, respectively.

### AOL Instant Typewriter Chat Service

To handle message passing, I will build a simple serverless chat app using AWS AppSync for managing the API and DynamoDB for managing chat messages, and Cognito for user authentication. By creating my own messaging service for the project, I can easily connect the typewriters and potentially external web-based users without needing to integrate 3rd party applications. Additionally, it will give me greater flexibility and allow me to do things like introduce message mutations in transit or fan messages out to other targets.
