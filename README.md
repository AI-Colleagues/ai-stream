# AI Stream

An AI app built with OpenAI and Streamlit. The necessary Streamlit widgets will be rendered according to your requests.

## Showcase

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-stream.streamlit.app/)

https://github.com/user-attachments/assets/96db4e0d-2792-4ca1-8065-ab8c80730d18

## Set up

Install:
```
poetry install
```

To set up, add `OPENAI_API_KEY` to your `.env` file.

## Run

Then type to start the app: `poetry run streamlit run ai_stream/app.py`


## TODO

* [x] Handle input data
* [x] Add more support for Streamlit widgets to create an MVP
* [ ] Add unit tests
* [ ] Add docs
* [ ] Add CI/CD
* [ ] Use multiple Assistants, e.g., separating UI and backend.
