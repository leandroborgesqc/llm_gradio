import os

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

SYSTEM_MESSAGE = (
    "You are a helpful assistant that responds in markdown without code blocks."
)
FOUNDRY_MODEL = "gpt-chat-latest"


def main():
    load_dotenv(override=True)

    google_api_key = os.getenv("GOOGLE_API_KEY")
    foundry_api_key = os.getenv("FOUNDRY_API_KEY")
    google_base_url = os.getenv("GOOGLE_BASE_URL")
    foundry_base_url = os.getenv("FOUNDRY_BASE_URL")

    if google_api_key:
        print(f"Google API Key exists and begins with {google_api_key[:3]}")
    else:
        print("Google API Key not set")

    if foundry_api_key:
        print(f"Foundry API Key exists and begins with {foundry_api_key[:3]}")
    else:
        print("Foundry API Key not set")

    google = OpenAI(api_key=google_api_key, base_url=google_base_url)
    foundry = OpenAI(api_key=foundry_api_key, base_url=foundry_base_url)

    message_input = gr.Textbox(
        label="Your message:", info="Enter a message for Foundry", lines=7
    )
    model_selector = gr.Dropdown(
        label="Model",
        choices=["Foundry", "Gemini"],
        value="Foundry",
        info="Select the model to use for generating responses",
    )
    message_output = gr.Markdown(label="Response:")

    def stream_model(prompt, model):
        if model == "Gemini":
            yield from message_gemini_stream(prompt, google)
        elif model == "Foundry":
            yield from message_foundry_stream(prompt, foundry)
        else:
            raise ValueError("Unknown model")

    view = gr.Interface(
        fn=stream_model,
        title="Microsoft Foundry",
        inputs=[message_input, model_selector],
        outputs=[message_output],
        examples=[
            ["Explain the Transformer architecture to a layperson", "Gemini"],
            ["Explain the Transformer architecture to an aspiring AI engineer", "Foundry"],
        ],
        flagging_mode="never",
        show_progress="full",
    )

    current_dir = os.path.dirname(os.path.abspath(__file__))
    favicon = os.path.join(current_dir, "favicon.ico")

    view.launch(inbrowser=True, favicon_path=favicon, theme="Ocean")


def message_foundry_stream(prompt, provider: OpenAI):
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": prompt},
    ]

    stream = provider.chat.completions.create(
        model=FOUNDRY_MODEL, messages=messages, stream=True
    )

    result = ""
    for chunk in stream:
        if not chunk.choices:
            continue

        result += chunk.choices[0].delta.content or ""
        yield result


def message_gemini_stream(prompt, provider: OpenAI):
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": prompt},
    ]

    stream = provider.chat.completions.create(
        model="gemini-3.1-flash-lite", messages=messages, stream=True
    )

    result = ""
    for chunk in stream:
        if not chunk.choices:
            continue

        result += chunk.choices[0].delta.content or ""
        yield result


if __name__ == "__main__":
    main()
