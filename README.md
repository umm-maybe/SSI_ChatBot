# Overview
This script is an extension/mash-up of the following projects:
1. https://github.com/zacc/ssi-bot
2. https://github.com/kaderator2/SubSimDiscordbot
3. https://github.com/scrubjay55/Reddit_ChatBot_Python

Basically, it allows an SSI GPT-2 bot fine-tuned on some selection of subreddits to engage with users via the Reddit real-time chat interface.  If you don't have an SSI bot yet, work through the steps detailed at link #1 above first to get one, then come back here.  All I essentially did is customize the example at link #3 with a slightly modified version of the text generation function in link #2.

# Installation
[Recommended] Create a virtual environment:

    python3 -m venv ssi_chatbot_env
    source ssi_chatbot_env/bin/activate

Install required dependencies:

    pip install torch
    pip install simpletransformers
    pip install Reddit-ChatBot-Python

Then, edit the script and change PATH_TO_MODEL, reddit username/password (for bot), and any other parameters as desired.

Run the script:

    python3 SSI_ChatBot.py

[Recommended] Monitor the chat to make sure your bot isn't saying anything naughty.
