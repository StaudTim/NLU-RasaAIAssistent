# Natural language understanding - AI Assistent using Rasa framework

This project was an exam for the module "assistance systems" as part of my studies in artificial intelligence. We had to use the rasa framework to create a chatbot that was supposed to simplify everyday life at the university in some way.

## Table of Contents

- [Install](#install)
- [Usage](#usage)


## Install

Install Rasa Open Source using pip requires Python 3.7 or 3.8 (I used Python 3.8.5 for this project). Installation instructions can be found on this website: https://rasa.com/docs/rasa/installation/


## Usage

#### Start Rasa server

Open your terminal and start your virtual environment. Navigate to the 'src' folder and enter the following command:


```sh

$ rasa run

```

#### Start AI Assistent

Open a new terminal in which you also start the virtual environment. Navigate to the 'src' folder and enter the following command:


```sh

$ rasa shell

```

This loads your trained model and lets you talk to your assistant on the command line.

