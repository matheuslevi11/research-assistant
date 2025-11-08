import os
import json
import logging
import fitz
import pandas as pd
from dotenv import load_dotenv
from docling.document_converter import DocumentConverter
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.utils.pprint import pprint_run_response
from src.agents.prompts import EXTRACTOR_SYSTEM_PROMPT, EXTRACTOR_PROMPT

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ExtractorAgent():
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm_model  = os.getenv("LLM_MODEL", "gpt-5-mini")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set in the .env file.")

        self.agent = Agent(
            model=OpenAIChat(id=self.llm_model, system_prompt=EXTRACTOR_SYSTEM_PROMPT),
        )

    def read_pdf_docling(self, pdf_filepath: str):
        """
        Reads and extracts text from a PDF file.
        """
        if not os.path.isfile(pdf_filepath):
            logging.error(f"PDF file not found: {pdf_filepath}")
            raise FileNotFoundError(f"PDF file not found: {pdf_filepath}")

        converter = DocumentConverter()
        doc = converter.convert(pdf_filepath).document
        return doc.export_to_markdown()

    def read_pdf(self, pdf_filepath: str):
        """
        Reads and extracts text from a PDF file.
        """
        doc = fitz.open(pdf_filepath, filetype="pdf")
        full_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            full_text += text
        doc.close()
        return full_text

    def save_json(self, data: dict, output_path: str):
        """
        Saves a dictionary as a JSON file to the specified output path.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logging.info(f"JSON data saved to {output_path}")

    def extract(self, pdf_filename: str) -> dict:
        """
        Processes a user query, searches for relevant documents, and generates a response.
        """
        pdf_directory = os.getenv("PDF_DIRECTORY", "")
        pdf_filepath = os.path.join(pdf_directory, pdf_filename)
        paper_content = self.read_pdf(pdf_filepath)
        message = EXTRACTOR_PROMPT.format(paper_content=paper_content)
        response = self.agent.run(message)
        pprint_run_response(response)

        result = response.content
        json_result = json.loads(result)
        return json_result

if __name__ == '__main__':
    library = pd.read_csv('/home/mlevi/Work/research-assistant/src/data/zotero_pdf_matches.csv', encoding='windows-1252')
    for i, row in library.iterrows():
        print(f'Executing {i+1} of {len(library)}')
        try:
            extractor_agent = ExtractorAgent()
            pdf_name = row['pdf_name']

            # Edge cases treatment
            if 'Parkinson' in pdf_name:
                pdf_name = pdf_name.replace("Parkinsons's", 'Parkinsons’s')
            if 'wavelet' in pdf_name:
                pdf_name = pdf_name.replace('diffusion-a', 'diffusion–a')

            extraction_output_path = os.path.join("extraction_outputs", f"{pdf_name.replace('.pdf', '')}_extraction.json")
            if not os.path.isfile(os.path.join(os.getenv("PDF_DIRECTORY", ""), pdf_name)):
                raise FileNotFoundError(f"PDF file not found: {pdf_name}")

            if not os.path.isfile(extraction_output_path):
                result = extractor_agent.extract(pdf_name)
                extractor_agent.save_json(result, extraction_output_path)
            else:
                logging.info(f"Extraction output already exists at {extraction_output_path}")

        except ValueError as ve:
            print(f"Configuration Error: {ve}")
        except FileNotFoundError as fnfe:
            print(f"File Error: {fnfe}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")