"""
agent.py — run this file to start chatting with your Dos Margaritas factory
agent in the terminal.

    python agent.py

What's actually happening here, in plain terms:

  - "anthropic" is Anthropic's official Python package for talking to
    Claude. `pip install anthropic` gets it.
  - `anthropic.Anthropic()` creates a client that knows how to send
    messages to Claude, using an API key it reads from the
    ANTHROPIC_API_KEY environment variable (see README.md for how to get
    one and set it).
  - `client.beta.messages.tool_runner(...)` is a helper that runs the
    whole "ask Claude -> Claude wants to use a tool -> run the tool ->
    tell Claude the result -> ask again" loop FOR you. Without it you'd
    have to write that loop by hand. It stops automatically once Claude
    has a final answer with no more tools to call.

This file has no business logic of its own — it just wires together the
tools (tools.py) and the conversation loop. That's on purpose: if you want
to add a new capability, you add a new @beta_tool function in tools.py and
put it in ALL_TOOLS. You should almost never need to touch this file.
"""

import os
import sys

import anthropic

from tools import ALL_TOOLS

# You can override the model without editing code by setting this env var,
# e.g.  FACTORY_AGENT_MODEL=claude-opus-5 python agent.py
# claude-sonnet-5 is a good default here: it's smart enough for this kind of
# task and much cheaper than Opus. See README.md for real cost numbers.
MODEL = os.environ.get("FACTORY_AGENT_MODEL", "claude-sonnet-5")

SYSTEM_PROMPT = """\
You are the factory agent for Dos Margaritas Salsa, a small family salsa
business. You help Michael (and Maggie) keep track of:
  - Interactions and orders with the stores that carry their salsa
  - Tasks and reminders
  - Quick reports and segmentation over the Master Store List

Always use your tools instead of guessing or making up numbers — if you
don't have a tool that can answer something, say so plainly instead of
inventing an answer. Keep replies short and practical; this is a working
tool, not a chatbot for its own sake.
"""


def print_message(message):
    """Show one turn of Claude's response in the terminal: the text it
    says, plus a small note whenever it decides to use a tool, so it's
    never a mystery what the agent is doing to your data."""
    for block in message.content:
        if block.type == "text" and block.text:
            print(block.text)
        elif block.type == "tool_use":
            print(f"  -> using tool: {block.name}({block.input})")


def main():
    # Check for the API key ourselves, up front, with a friendly message —
    # otherwise the SDK's own error about it is a big scary traceback,
    # which isn't a great first experience.
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY isn't set, so there's no way to reach Claude yet.")
        print("See README.md for how to get a key and set it, then try again.")
        sys.exit(1)

    client = anthropic.Anthropic()

    print("Dos Margaritas factory agent. Type 'exit' to quit.\n")

    messages = []
    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            break

        messages.append({"role": "user", "content": user_input})

        runner = client.beta.messages.tool_runner(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=ALL_TOOLS,
            messages=messages,
        )

        last_message = None
        try:
            for message in runner:
                print_message(message)
                last_message = message
        except Exception as e:
            # Anything from a network hiccup to a bad request shows up here.
            # We catch it broadly so one bad turn doesn't crash your whole
            # chat session — you can just try again.
            print(f"(Something went wrong: {e})")
            messages.pop()  # drop the user turn that failed, so it isn't sent twice
            continue

        # tool_runner keeps its own internal copy of the conversation, but
        # doesn't hand it back to us — so we track the final assistant turn
        # ourselves and append it, keeping our own `messages` list complete
        # for the next round of input.
        if last_message is not None:
            messages.append({"role": "assistant", "content": last_message.content})


if __name__ == "__main__":
    main()
