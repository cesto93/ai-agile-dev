FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy only dependency files first
COPY pyproject.toml ./

# Generate requirements.txt if using pyproject.toml
RUN uv pip compile pyproject.toml -o requirements.txt

# Install dependencies
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "-m", "streamlit","run","src/ui.py"]
