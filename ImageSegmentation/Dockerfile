# Use an official Python 3.11 runtime as a base image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install dependencies for OpenCV
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Copy the requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install -r requirements.txt
# Ensure all files in /app have read and execute permissions
RUN chmod -R 755 /app


# Copy the Django project files
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Command to run Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
