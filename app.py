"""A test app. """

import openai
import streamlit as st
from openai.error import AuthenticationError, InvalidRequestError


APP_TITLE = "Tekosu"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.info("""このアプリはご覧のスポンサーの提供でお送りします。
- [OpenAI](https://openai.com/)
- [Streamlit](https://streamlit.io/)
- [Python](https://python.org/)
""")

st.sidebar.header("Configuration")

st.sidebar.write("You must provide your own OpenAI key.")
openai.api_key = st.sidebar.text_input(
    "OpenAI API key",
    type="password",
    autocomplete="current-password",
)

error = st.container()

try:
  openai_models = [model["id"] for model in openai.Model.list()["data"]]  # type: ignore
except AuthenticationError as e:
  openai_models = []

  if openai.api_key:
    error.error(e)

CHAT_MODELS = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"]

available_models = sorted(list(set(openai_models) & set(CHAT_MODELS)))
try:
  default_model_index = available_models.index("gpt-3.5-turbo")
except ValueError:
  default_model_index: int = 0

openai_model = st.sidebar.selectbox(
    "Model",
    options=available_models,
    index=default_model_index,
    help='Only available models are shown.',
)

use_top_p = st.sidebar.checkbox("Set randomness via top *p*")
if use_top_p:
  top_p = st.sidebar.slider(
      "Top *p*",
      min_value=0.0,
      max_value=1.0,
      step=0.05,
      value=0.5,
      help='Controls the "randomness" of responses.',
  )
else:
  temperature = st.sidebar.slider(
      "Temperature",
      min_value=0.0,
      max_value=1.0,
      step=0.05,
      value=0.1,
      help='Controls the "randomness" of responses.',
)


def translate(text: str) -> str:
  """Translates legalese to English."""
  if not text.strip():
    return ""

  try:
    response = openai.ChatCompletion.create(
        model=openai_model,
        temperature=temperature if not use_top_p else None,
        top_p=top_p if use_top_p else None,
        messages=[
            {
              "role": "user",
              "content": f"""
  Summarize the following terms and conditions, highlighting key clauses.

  ```
  {legalese}
  """,
            }
        ],
    )

    return response["choices"][0]["message"]["content"]  # type: ignore
  except InvalidRequestError as invalid_request:
    error.error(invalid_request)

    return ""


st.title(APP_TITLE)
st.write("Terms and conditions made easy—unravel the fine print in just a few keystrokes.")
st.divider()

col1, col2 = st.columns(2)
legalese = col1.text_area(
    "Input",
    label_visibility="collapsed",
    placeholder="Paste something here",
    height=600,
)
col2.text_area(
    "Translation",
    label_visibility="collapsed",
    placeholder="The translation will appear here",
    height=600,
    value=translate(legalese),
    disabled=True,
)
