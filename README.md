# AI Stream

An AI app built with OpenAI and Streamlit. The necessary Streamlit widgets will be rendered according to your requests.

## Showcase

https://github.com/user-attachments/assets/96db4e0d-2792-4ca1-8065-ab8c80730d18

## Set up

Install:
```
pip install -e .
```

To set up, add `OPENAI_API_KEY` to your `.env` file.

## Run

Start moto server first (for local DynamoDB): `moto_server`.

Then type to start the app: `streamlit run ai_stream/app.py`


## TODO

* [x] Handle input data
* [x] Add more support for Streamlit widgets to create an MVP
* [ ] Add unit tests
* [ ] Add docs
* [ ] Add CI/CD
* [ ] Use multiple Assistants, e.g., separating UI and backend.
