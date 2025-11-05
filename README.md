# Academic Research Assistant

This project is an intelligent agent designed to assist researchers in the challenging task of identifying, reading, analyzing, and synthesizing knowledge from a bibliographic review. The agent acts as a "personal research assistant," connecting directly to the user's Zotero library. It can process the full text of articles (in PDF format), extract key information, build a knowledge base, and allow the researcher to interact with their own library of articles through a natural language interface.

The idea is to assist in complex cognitive tasks, such as information synthesis, identification of common methodologies, and discovery of gaps in the literature, significantly accelerating the literature review process.

## Features

- **Zotero Integration:** Connects to your Zotero library to access your research papers.
- **PDF Processing:** Extracts text and metadata from PDF files.
- **Vector Database:** Uses Qdrant to store and search paper embeddings.
- **Conversational AI:** A Streamlit-based web interface to ask questions about your research papers.
- **Automatic Analysis:** An analyzer agent that automatically processes papers, generating summaries and structured data.

## How it Works

The project is composed of a few key components that work together to provide the research assistant functionality:

```
+-----------------+      +-----------------+      +-----------------+
|                 |      |                 |      |                 |
|  Zotero Library |----->| Analyzer Agent  |----->|  Vector Database|
|                 |      | (PDF Processing)|      |    (Qdrant)     |
+-----------------+      +-----------------+      +-----------------+
        ^                                                 ^
        |                                                 |
        |                                                 |
+-----------------+      +----------------------+
|                 |      |                      |
| Web Interface   |<---->| Conversational Agent |
|  (Streamlit)    |      |                      |
+-----------------+      +----------------------+
```

1.  **Zotero Integration:** The `zotero_integration.py` script connects to the Zotero API and fetches the metadata of the articles in your library.
2.  **Analyzer Agent:** The `analyzer_agent.py` script processes each PDF file, extracts the text, and uses a large language model to generate a summary and a structured JSON file with key information (e.g., methodologies, datasets, etc.).
3.  **Vector Database:** The `vector_database.py` script creates a Qdrant collection and upserts the embeddings of the processed papers, creating a searchable knowledge base.
4.  **Conversational Agent:** The `conversational_agent.py` script provides a conversational interface that takes user queries, searches the knowledge base, and generates answers.
5.  **Web Interface:** The `app.py` script provides a user-friendly web interface using Streamlit, allowing you to interact with the conversational agent.

## Getting Started

To get started with this project, you'll need to have the following installed:

- Python 3.10+
- Docker
- uv

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/research-assistant.git
    cd research-assistant
    ```

2.  **Install dependencies:**

    ```bash
    uv sync
    ```

3.  **Set up environment variables:**

    Create a `.env` file in the root of the project and add the following variables:

    ```
    OPENAI_API_KEY="your-openai-api-key"
    ZOTERO_USER_ID="your-zotero-user-id"
    ZOTERO_API_KEY="your-zotero-api-key"
    PDF_DIRECTORY="/path/to/your/pdfs"
    ```

4.  **Run the database:** (TODO: Write Docker Compose)

    ```bash
    docker-compose up -d
    ```

5.  **Run the application:** (Work in Progress)

    ```bash
    uv run ui/app.py
    ```

## Usage

Once the application is running, you can open your web browser and navigate to `http://localhost:8501`. You will see a chat interface where you can ask questions about your research papers.

For example, you can ask:

- "What is the main contribution of the paper 'Paper Title'?"
- "What are the main datasets used for evaluating classification algorithms?"
- "Compare the approaches of authors A and B on the topic of..."

## Project Structure

```
.
├── analysis_outputs/   # Output of the analyzer agent
├── qdrant_storage/     # Qdrant vector database storage
├── src/
│   ├── agents/         # Analyzer and conversational agents
│   ├── data/           # Zotero integration and vector database
│   └── main.py         # Main application
└── ui/
    └── app.py          # Streamlit web interface
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
