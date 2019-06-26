FROM python:3.7
ADD . /code
WORKDIR /code
RUN pip install redis flask
CMD ["python3", "/code/venv/Include/MyOrder.py"]
