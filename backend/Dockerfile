# Use an official Python runtime
FROM python:3.9

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

# Expose port
EXPOSE 5000

# Run Flask in development mode
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
