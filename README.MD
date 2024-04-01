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

### Linux

```
./run.sh
```

### Windows

```
./run.ps1
```
