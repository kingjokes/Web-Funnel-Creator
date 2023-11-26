FROM python:3.9

WORKDIR /usr/sycart/python

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

# install dependencies  
RUN pip install --upgrade pip

COPY requirements.txt ./ 

RUN pip install -r requirements.txt
COPY . ./

EXPOSE 8000