
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --no-input

# Make migrations
RUN python manage.py makemigrations

# Apply migrations 
RUN python manage.py migrate

# Start server
CMD python manage.py runserver 0.0.0.0:8000