# Use an official PyPy runtime as a parent image
FROM pypy:3-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Expose the port Gunicorn will run on
EXPOSE 8000

# Define environment variable
ENV FLASK_ENV production

# Run Gunicorn
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "app:app"]
