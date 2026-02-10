FROM python:3.9

# Create user with correct permissions
RUN useradd -m -u 1000 user
WORKDIR /app

# Copy requirements first for better caching
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application
COPY --chown=user . /app

# Switch to non-root user (important for Spaces)
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Run the application with main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
