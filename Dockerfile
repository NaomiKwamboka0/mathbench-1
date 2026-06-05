FROM python:3.11-slim

WORKDIR /app

# Install dependencies first so this layer is cached across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project.
COPY . .

# Backend is auto-selected: 'gemini' if GEMINI_API_KEY is provided, else
# 'claude' if ANTHROPIC_API_KEY is provided, else the offline 'reference'
# oracle (so the image runs even with no key at all).
ENV PYTHONUNBUFFERED=1

# Run the full benchmark by default. Override the CMD to run tests, e.g.
#   docker run mathbench-1 python -m tests.test_mathbench
CMD ["python", "run_benchmark.py"]
