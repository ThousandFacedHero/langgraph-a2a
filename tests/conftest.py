"""Shared pytest fixtures and configuration.

Set OPENAI_API_KEY and OPENAI_BASE_URL in .env or environment
before running tests that make real LLM calls.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("OPENAI_BASE_URL", "http://localhost:11434/v1")
os.environ.setdefault("SSL_CERT_FILE", "")
