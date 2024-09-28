FROM python:3.12
WORKDIR /app
COPY  ./charcreator_backend /app/charcreator_backend
COPY  ./requirements.txt /app/requirements.txt
COPY ./main.py /app/main.py
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
CMD ["fastapi", "run", "main.py", "--port", "80"]