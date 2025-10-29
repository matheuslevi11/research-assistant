import os
import typer
import logging
from dotenv import load_dotenv
from rich.prompt import Prompt
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.data.vector_database import load_database
from src.agents.prompts import CONVERSATIONAL_SYSTEM_PROMPT, CONVERSATIONAL_PROMPT

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConversationalAgent():
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm_model  = os.getenv("LLM_MODEL", "gpt-5-mini")
        self.knowledge = load_database(os.getenv("PDF_DIRECTORY", ""), skip_add=True)
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set in the .env file.")

        self.agent = Agent(
            model=OpenAIChat(id=self.llm_model, system_prompt=CONVERSATIONAL_SYSTEM_PROMPT),
            knowledge=self.knowledge,
            search_knowledge=True,
            instructions=[
                "Always search your knowledge base before answering questions",
                "Include source references in your responses when possible"
            ]
        )

    def run(self, user: str = "Levi"):
        """
        Processes a user query, searches for relevant documents, and generates a response.
        """
        while True:
            message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
            if message in ("exit", "bye"):
                break
            self.agent.print_response(message)

if __name__ == '__main__':
    try:
        conversational_agent = ConversationalAgent()
        typer.run(conversational_agent.run)
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
