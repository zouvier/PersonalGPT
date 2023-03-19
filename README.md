# PersonalGPT

Built this out so that i could have a better control over my conversations with GPT-4. 
currently, it supports conversation history management, including search, and exporting.

## Features

- User-friendly interface for text generation using OpenAI's GPT models
- Response options: temperature control, model selection (e.g., gpt-4, gpt-4-32k, gpt-3.5-turbo)
- Conversation history management
  - Save, search, and filter conversation history
  - Sort by chronological order
  - Pagination for better readability
  - Export conversation history as a CSV file
  - Clear conversation history
- Sidebar with tabs for Response Options and Conversation History

## Installation

1. Clone the repository:

   - `git clone https://github.com/zouvier/PersonalGPT`
   - `cd PersonalGPT`


2. Install the required dependencies:

   - `pip install -r requirements.txt`


3. Set up your OpenAI API key and organization:

   - Create a `.env` file in the project directory and add the following lines: 
     - OPENAI_API_KEY=your_openai_api_key 
     - OPENAI_ORGANIZATION=your_openai_organization

Replace `your_openai_api_key` and `your_openai_organization` with your actual API key and organization.

4. Run the Streamlit app:


5. Open the app in your web browser by navigating to the URL displayed in the terminal (usually http://localhost:8501).

## Usage

1. Enter your input in the "Input" field.
2. Optionally, adjust the response options (temperature, model) in the "Response Options" tab in the sidebar.
3. Click "Submit" to generate the output.
4. View the generated output in the "Output" section.
5. Manage conversation history using the "Conversation History" tab in the sidebar.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

