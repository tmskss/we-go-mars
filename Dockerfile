FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .
COPY README.md .

# Install dependencies
RUN uv pip install --system -e .

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Set Python path
ENV PYTHONPATH=/app

# Default command
CMD ["python", "-m", "src.main"]
