# Chatbot with Personality

This is a seq2seq with attention deep learning model for training a chatbot. After training, there is a command line interface to support chat.

## Installation

1. Clone this repo to your local machine.
2. Requirements are numpy and tensorflow. Run "pip install -r requirements.txt" from the terminal within the project directory to install requirements.

 ## Usage

1. Model is currently untrained. Run "python chatbot.py --mode train1" to train on Cornell Movie dialogue corpus, "python chatbot.py --mode train2" to train on Big Bang Theory Transcripts, or "python chatbot.py --mode train3" to train on only Sheldon responses.
Paramters will be saved in the checkpoints folder. Delete checkpoints files to train from scratch.
2. Run "python chatbot.py --mode chat" to chat from the command line. Conversations will be saved in the "processed" folder

## Credits
Inspiration from Google's Translation Model, Chip Huyen, Sanduriyadeepan Ram
