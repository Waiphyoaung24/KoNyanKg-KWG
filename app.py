"""
Gemini RAG Application

A real-time RAG application using Pathway with Gemini LLM and embeddings.
Provides always up-to-date knowledge from indexed documents.

Usage:
    python app.py

Endpoints:
    POST /v1/retrieve      - Search documents without LLM
    POST /v1/statistics    - Index health stats
    POST /v2/list_documents - List all indexed files
    POST /v2/answer        - Ask questions (RAG)
    POST /v2/summarize     - Summarize texts
"""

import os
from dotenv import load_dotenv

import pathway as pw
from pathway.xpacks.llm.question_answering import BaseRAGQuestionAnswerer
from pathway.xpacks.llm.servers import QASummaryRestServer
from pydantic import BaseModel, ConfigDict, InstanceOf

# Load environment variables
load_dotenv()

# Set Pathway license key (using demo key for development)
pw.set_license_key(os.getenv("PATHWAY_LICENSE_KEY", "demo-license-key-with-telemetry"))


class App(BaseModel):
    """Application configuration model."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    question_answerer: InstanceOf[BaseRAGQuestionAnswerer]
    host: str = "0.0.0.0"
    port: int = 8000
    with_cache: bool = True
    terminate_on_error: bool = False

    def run(self) -> None:
        """Start the REST server."""
        server = QASummaryRestServer(self.host, self.port, self.question_answerer)
        server.run(
            with_cache=self.with_cache,
            terminate_on_error=self.terminate_on_error,
            cache_backend=pw.persistence.Backend.filesystem(".cache"),
        )


def main():
    """Load configuration and run the application."""
    print("=" * 60)
    print("Gemini RAG Application")
    print("=" * 60)
    print(f"Loading configuration from app.yaml...")

    # Load configuration from YAML
    with open("app.yaml") as f:
        config = pw.load_yaml(f)

    print(f"Starting server on {config.get('host', '0.0.0.0')}:{config.get('port', 8000)}")
    print("=" * 60)
    print("Available endpoints:")
    print("  POST /v1/retrieve       - Search documents")
    print("  POST /v1/statistics     - Index health stats")
    print("  POST /v2/list_documents - List indexed files")
    print("  POST /v2/answer         - Ask questions (RAG)")
    print("  POST /v2/summarize      - Summarize texts")
    print("=" * 60)

    # Create and run app
    app = App(**config)
    app.run()


if __name__ == "__main__":
    main()
