# Use an official Python runtime as a parent image
#FROM nvcr.io/nvidia/pytorch:23.07-py3
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /home/bewinter/app_SPT

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements.txt first to leverage Docker cache
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your application code after the pip install
COPY . .

# Change working folder
WORKDIR /home/bewinter/app_SPT/src

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
#ENV PORT=8080

# Run app.py when the container launches
CMD ["sh", "-c", "streamlit run --server.port $PORT spt_app.py"]
