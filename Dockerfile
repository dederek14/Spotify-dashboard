# Use official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory inside container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project code into the container
COPY . /app/

# Expose port (default Django runs on 8000)
EXPOSE 8000

# Command to run your Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
