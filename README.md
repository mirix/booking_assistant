# Appointment booking assistant

A mock exercise towards an AI-powered appointment booking assistant.

Not perfect but fully functional.

The goal of the first versions was to rely purely on LLMs. That strategy failed.

The current version is inspired by the opposite strategy: rely on the LLM only for conversation and tool calling. The more deterministic/heuristic work is handled by ad hoc functions.

Each approach presents advantages and disadvantages: whereas the first approach was low-code and easy to maintain, the current approach is leaner and far more reliable.

## Caveats and Limitations

- Searching and booking only. Functionality for cancelling or reschedulling appointments has not been implemented.

- Policies are not vectorised because the model showcases a 128k context window and it seems to work better without vectorisation.

## Self-imposed goals

- Clear low-code approach.

- Simple and understandable structure.

- Fully on-premises: no internet access required if the poetry environment were provided (it is not the case).

- Modularity.

- Scalability.

## Stack of technologies

- Ollama: run quantised models locally.

- LangChain: agent creation.

- Streamlit for the chatbot GUI

- Microsoft Recognizers (recognizers-date-time) for parsing natural language timestamps.

# Hardware requirements

- NVIDA card with at least 24 GB of VRAM (see below in case of memory constraints).

- At least 10 GB of hardrive space to store the environment and the model.

# Software requirements

- Tested with Python 3.12.6.

- Tested on Linux 6.10.13-3-MANJARO #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux

- [Ollama](https://github.com/ollama/ollama/blob/main/docs/linux.md)

- CUDA (tested on version 12.6) and matching GPU drivers (tested on version 560.35.03).

## Installation

0. Clone this repo.

1. Install Ollama:

[Ollama](https://github.com/ollama/ollama)

2. Deploy the models for local use:

```bash
ollama pull hf.co/bartowski/Qwen2.5-Coder-32B-Instruct-GGUF:Q4_K_M
```

3. If you are here you have already downloaded and unzipped the git repository. cd into it.

4. Create and activate a python environment outside of the git repo (change name and path as desired):

```bash
python -m venv ../appointment_assistant
```
```bash
source ../infinit/bin/appointment_assistant
```
```bash
pip install --upgrade pip
```

5. Install requirements:

```bash
pip install -r requirements.txt
```

### Files

- appointment_assistant.py      Main chatbot script
- book_appointment.py           Appointment booking tool
- date_search.py                Available slots search tool
- random_calendar.csv           Sample calendar in CSV format
- random_calendar.json          Sample calendar in JSON format
- random_calendar.py            Auxiliary script to generate a random calendar according to the specifications in JSON and CSV formats
- README.md                     This README FILE
- requirements.txt              Dependencies


## Running the Project

Launch the streamlit chatbot from the root folder of your project:

```bash
streamlit run appointment_assistant.py
```

CRTL+Click on the URL that appears on the console and the chatbot should open on your default browser.


## Support

More information on the provided video.

Call me or email me for further discussion. I would really appreciate your feedback.

