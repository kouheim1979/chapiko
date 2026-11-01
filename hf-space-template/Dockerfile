FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=7860

# CPU版torchを先に入れる（PyPIの通常版はGPU用で数GBあり、無料Spaceのビルドが重くなる）
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Hugging Face Spaceはコンテナを UID 1000 で動かす。
# HOMEを書き込める場所にしないと、モデルのダウンロード先(~/.cache)で Permission denied になる。
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    HF_HOME=/home/user/.cache/huggingface
WORKDIR /home/user/app

COPY --chown=user app.py .

EXPOSE 7860

CMD ["python", "app.py"]
