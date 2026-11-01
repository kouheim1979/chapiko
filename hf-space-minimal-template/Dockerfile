FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=7860

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Hugging Face Spaceはコンテナを UID 1000 で動かすので、同じユーザーを作っておく
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user
WORKDIR /home/user/app

COPY --chown=user app.py .

EXPOSE 7860

CMD ["python", "app.py"]
