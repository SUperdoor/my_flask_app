FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y wkhtmltopdf

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
