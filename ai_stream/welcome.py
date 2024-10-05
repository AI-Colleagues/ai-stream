"""Welcome page."""

import streamlit as st


def main():
    """App layout."""
    st.title("Welcome to AI Stream")
    st.write(
        """
        Read the following Q&A to get an idea of AI Stream.

        ### What is AI Stream?

        AI Stream is designed to help you complete various tasks through
        conversations with AI assistants. Whether you need to specify a time,
        upload a file, select an option, or display the output as a table, line
        chart, or pyplot, AI Stream delivers results just-in-time.

        ### How is AI Stream built?

        You might wonder, "How is this possible?" The answer lies in the AI
        assistant that powers the app, which renders all input and output
        widgets through function calls.

        ### Can I try it without providing my API key?

        To simplify things, we've created Random Stream—essentially AI Stream,
        but without the AI. Give it a try, and you'll see input and output
        widgets being randomly displayed. Now, imagine all your requests being
        accurately answered with text, images, or other input/output widgets.
        That's what we aim for AI Stream to achieve.

        ### What is Assistant Assembly?

        OpenAI assistants are the "secret sauce" behind AI Stream. To make it
        work, or to customize your own assistant, you'll need to create or
        select a prompt, choose some tools for it to use, and then assemble
        them with the assistant.

        ### Can't I configure assistants in the OpenAI Playground?

        Yes, you can. However, you'll still need AI Stream or your own clone to
        make it work seamlessly. Another benefit of using the Assembly pipeline
        in AI Stream is the auto-update feature. If you update a tool used by
        multiple assistants, you likely won't want to update each one manually
        in the OpenAI Playground. With AI Stream, all assistants using that
        tool are automatically updated, like an "OTA update" for your
        assistants.
        """
    )


main()
