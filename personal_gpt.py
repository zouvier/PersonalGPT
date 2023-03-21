import os
import json
import base64
import concurrent.futures
import pandas as pd
import streamlit as st
import openai
import re

# Load environment variables from .env file

# Set up your OpenAI API key and organization
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORGANIZATION")
tab1, tab2 = st.sidebar.tabs(["Response Options", "Conversation History"])

@st.cache_data()
def generate_output(prompt, temperature=0.5, model="gpt-4"):
    """Generate output using the OpenAI API."""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            n=1,
            stop=None,
            temperature=temperature
        )
        message = response.choices[0].message.content
        return message
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def generate_outputs(prompts, model, temperature=0.5, max_workers=5):
    """Generate outputs for multiple prompts using the OpenAI API."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(generate_output, prompt, temperature, model) for prompt in prompts]
        return [future.result() for future in concurrent.futures.as_completed(futures)]


def load_history():
    """Load conversation history from a JSON file."""
    try:
        with open('history.json', 'r') as file:
            history = json.load(file)
    except FileNotFoundError:
        history = []
    return history


def save_history(history):
    """Save conversation history to a JSON file."""
    with open('history.json', 'w') as file:
        json.dump(history, file)


def filter_history(history, search_term):
    """Filter conversation history based on the search term."""
    if search_term is None or search_term.strip() == "":
        return history
    return [entry for entry in history if search_term.lower() in (entry["user"] or "").lower() or search_term.lower() in (entry["bot"] or "").lower()]


def export_history(history):
    """Export conversation history as a CSV file."""
    df = pd.DataFrame(history)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="conversation_history.csv">Download CSV File</a>'

def generate_unique_title(title, history):
    """Generate a unique title for the conversation."""
    unique_title = title
    titles_in_history = [entry["title"] for entry in history]

    match = re.search(r'(\d+)$', title)
    if match:
        counter = int(match.group(1)) + 1
        unique_title = re.sub(r'\d+$', '', title).strip()
    else:
        counter = 2

    while unique_title in titles_in_history or f"{unique_title} {counter}" in titles_in_history:
        unique_title = re.sub(r'\d+$', '', unique_title).strip()
        unique_title = f"{unique_title} {counter}"
        counter += 1

    return unique_title


def build_ui():
    """Build the Streamlit user interface."""
    st.title("OpenAI API Streamlit App")
    st.write("Enter your input and let the OpenAI API generate an output.")

    history = load_history()

    # Add a dropdown menu for selecting previous conversations
    previous_conversations = ["None"] + [entry["title"] for entry in history]
    selected_conversation = st.selectbox("Select a previous conversation that you want to continue:", previous_conversations)
    conversation_title = st.text_input("Title:")
    conversation_title = generate_unique_title(conversation_title, history)

    if selected_conversation != "None":
        user_input = st.text_input("Input:") + "Previous conversation:" + selected_conversation
    else:
        user_input = st.text_input("Input:")

    # Add a title input field for the conversation


    tab1.header("Response Options")
    temperature = tab1.slider("Temperature:", min_value=0.1, max_value=1.0, value=0.5, step=0.1)
    model = tab1.selectbox("Model", ("gpt-4", "gpt-4-32k", "gpt-3.5-turbo"))

    if 'output' not in st.session_state:
        st.session_state.output = ''

    # Create columns for the buttons and checkbox
    col1, col2, col3 = st.columns(3)

    submit_button = col1.button("Submit")
    reset_button = col2.button("Reset")

    # Add a button for not saving the conversation
    do_not_save_button = col3.checkbox("Do not save to history")

    if reset_button:
        user_input = ""
        st.session_state.output = ""

    if user_input and submit_button:
        if user_input.strip() == "":
            st.error("Please enter a valid input.")
        else:
            prompts = [user_input]
            with st.spinner("Generating output..."):
                outputs = generate_outputs(prompts, model, temperature)

            if outputs:
                for i, output in enumerate(outputs):
                    # Append the conversation with the title to the history only if the do_not_save_button is not pressed
                    if not do_not_save_button:
                        history.append({"title": conversation_title, "user": prompts[i], "bot": output})
                        save_history(history)

                st.session_state.output = outputs[0]

    st.write("Output:")
    st.write(st.session_state.output)

    build_conversation_history_ui(history)



def build_conversation_history_ui(history):
    """Build the conversation history user interface."""
    tab2.header("Conversation History")

    # Display the number of saved conversations
    tab2.write(f"Number of saved conversations: {len(history)}")
    entries_per_page = tab2.slider("Entries per page:", min_value=1, max_value=10, value=5, step=1)

    col1, col2 = tab2.columns(2)

    if col1.button("Export Conversation History"):
        col1.markdown(export_history(history), unsafe_allow_html=True)

    if col2.button("Clear Conversation History"):
        history = [{"title": "Instructions",
                    "user": "this is you",
                    "bot": "this is the response from GPT-# "}]
        save_history(history)
        tab2.success("Conversation history cleared.")

    search_term = tab2.text_input("Search:")
    filtered_history = filter_history(history, search_term)

    # Add a checkbox for sorting history in chronological order
    chronological_order = tab2.checkbox("Sort by chronological order")

    # Sort the filtered history based on the checkbox value
    if chronological_order:
        filtered_history.reverse()


    num_pages = len(filtered_history) // entries_per_page + (1 if len(filtered_history) % entries_per_page > 0 else 0)
    page = tab2.number_input("Page:", min_value=1, max_value=num_pages, value=1, step=1)
    start_index = (page - 1) * entries_per_page
    end_index = start_index + entries_per_page

    for entry in filtered_history[start_index:end_index]:
        # Use st.expander to create an expandable widget for each conversation
        with tab2.expander(f'Title: {entry["title"]}'):
            st.write(f'User: {entry["user"]}')
            st.write(f'Bot: {entry["bot"]}')
            st.write("---")



def main():
    build_ui()


if __name__ == "__main__":
    main()