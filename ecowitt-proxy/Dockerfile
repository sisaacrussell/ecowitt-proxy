FROM python:3.12-alpine3.24

WORKDIR /app
RUN python -m pip install --no-cache-dir \
    'Flask>=3.1.3' 'Werkzeug>=3.1.9' 'requests>=2.34.2' 'urllib3>=2.8.0'

COPY app/ /app
RUN chmod +x /app/run.sh

CMD ["./run.sh"]
