FROM python:3.11

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . ./

WORKDIR /usermanagement

EXPOSE 8000

# CMD ["python", "manage.py", "runserver"]
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000 & celery -A usermanagement.celery_app worker --loglevel=info & celery -A usermanagement.celery_app beat --loglevel=info"]