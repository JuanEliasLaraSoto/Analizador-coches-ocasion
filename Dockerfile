FROM python:3.12-slim

# uv: el gestor de paquetes del proyecto
RUN pip install --no-cache-dir uv==0.8.17

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_NO_CACHE=1

# 1) Dependencias: esta capa solo se rehace si cambian pyproject.toml o uv.lock
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) Código, web y modelo entrenado
COPY src ./src
COPY web ./web
COPY modelos ./modelos
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH" PORT=7860
EXPOSE 7860

# Usuario sin privilegios (Hugging Face Spaces usa el UID 1000)
RUN useradd -m -u 1000 app
USER app

CMD ["sh", "-c", "uvicorn ocasion.api:app --host 0.0.0.0 --port ${PORT}"]
