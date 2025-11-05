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
from src.agents.prompts import ANALYZER_SYSTEM_PROMPT, ANALYZER_PROMPT

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AnalyzerAgent():
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm_model  = os.getenv("LLM_MODEL", "gpt-5-mini")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set in the .env file.")

        self.agent = Agent(
            model=OpenAIChat(id=self.llm_model, system_prompt=ANALYZER_SYSTEM_PROMPT),
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

    def get_cached_metadata(self, pdf_filename: str) -> dict | None:
        """
        Retrieves cached metadata for a given PDF filename.
        """
        cache_dir = os.getenv("ZOTERO_CACHE_DIR", "zotero_cache_metadata")
        cache_filepath = os.path.join(cache_dir, f"{pdf_filename.replace('.pdf', '')}.json")
        if os.path.isfile(cache_filepath):
            with open(cache_filepath, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return metadata
        return None

    def save_result(self, result: str, output_path: str):
        """
        Saves the analysis result to a specified output path.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        logging.info(f"Analysis result saved to {output_path}")

    def save_json(self, data: dict, output_path: str):
        """
        Saves a dictionary as a JSON file to the specified output path.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logging.info(f"JSON data saved to {output_path}")

    def analyze(self, pdf_filename: str):
        """
        Processes a user query, searches for relevant documents, and generates a response.
        """
        pdf_directory = os.getenv("PDF_DIRECTORY", "")
        pdf_filepath = os.path.join(pdf_directory, pdf_filename)
        paper_content = self.read_pdf(pdf_filepath)
        paper_metadata = self.get_cached_metadata(pdf_filename) or {}
        message = ANALYZER_PROMPT.format(paper_metadata=paper_metadata, paper_content=paper_content)
        response = self.agent.run(message)
        pprint_run_response(response)

        result = response.content
        filtered_string = result[result.find("## Question Answering"): ]
        qa_json = filtered_string[filtered_string.find("{"): filtered_string.find("}")+1].replace('\n', ' ')
        qa_json = json.loads(qa_json)
        return result, qa_json

if __name__ == '__main__':
    library = pd.read_csv('/home/mlevi/Work/research-assistant/src/data/zotero_pdf_matches.csv', encoding='windows-1252')
    for i, row in library.iterrows():
        print(f'Executing {i+1} of {len(library)}')
        try:
            analyzer_agent = AnalyzerAgent()
            pdf_name = row['pdf_name']

            # Edge cases treatment
            if 'Parkinson' in pdf_name:
                pdf_name = pdf_name.replace("Parkinsons's", 'Parkinsons’s')
            if 'wavelet' in pdf_name:
                pdf_name = pdf_name.replace('diffusion-a', 'diffusion–a')
            analysis_output_path = os.path.join("analysis_outputs", f"{pdf_name.replace('.pdf', '')}_analysis.md")
            if not os.path.isfile(os.path.join(os.getenv("PDF_DIRECTORY", ""), pdf_name)):
                raise FileNotFoundError(f"PDF file not found: {pdf_name}")

            if not os.path.isfile(analysis_output_path):
                result, qa_json = analyzer_agent.analyze(pdf_name)
                analyzer_agent.save_result(result, analysis_output_path)
                analyzer_agent.save_json(qa_json, analysis_output_path.replace('_analysis.md', '_qa.json'))
            #else:
                #logging.info(f"Analysis output already exists at {analysis_output_path}")
        except ValueError as ve:
            print(f"Configuration Error: {ve}")
        except FileNotFoundError as fnfe:
            print(f"File Error: {fnfe}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")