"""Welcome page."""

import streamlit as st


def main():
    """App layout."""
    st.title("Welcome to AI Stream")
    st.write(
        """
        Read the following Q&A to get an idea of AI Stream.

        ## What is AI Stream?

        AI Stream aims to accomplish many of your tasks through a conversation
        with AI assistants. If you need to specify a time, upload a file,
        select an option, or if you want to see the output as a table, line
        chart, pyplot, AI Stream does it on demand.

        ## How is AI Stream built?

        "How is it possible?" you may ask. The answer is that the AI assistant
        powering this app renders all input/output widgets through function
        calls.

        ## Can I try it without giving my API key?

        To make it simple, we've also built Random Stream, which is AI Stream
        but without AI, hope it makes sense. Try talking to it, and you will
        see input and output widgets being randomly displayed. Now imagine that
        all your requests are accurately replied with texts, images, or input/
        output widgets. And that's what we want AI Stream to do.

        ## What is Assistant Assembly?

        OpenAI Assistants are the secret sauce behind AI Stream. To make it
        work, or to customise your own assistant, you need to create or select
        a prompt, create or select some tools for it to use, and then assemble
        them together with an assistant.

        ## Can't I configure assistants on my OpenAI playground?

        You can, but you still need AI Stream or run your clone to get it work.
        Besides, another advantage of using the Assembly pipeline in AI Stream
        is the auto update. Imagine you updated a tool definition that's used
        by multiple assistants, you probably don't want to update them manually
        on OpenAI playground. Doing it here, AI Stream automatically updates
        all the assistants using this tool, sort of an "OTA update" to the
        assistants.
        """
    )


main()
