#!/bin/bash
# Sube a tu Space de Hugging Face SOLO los archivos que necesita la web.
# Nunca sube .env (tu clave), .venv, los datos ni los experimentos.
#
# Uso:  ./scripts/publicar.sh TU-USUARIO-DE-HUGGING-FACE
set -e

USUARIO="$1"
SPACE="analizador-coches-ocasion"

if [ -z "$USUARIO" ]; then
  echo "Uso: ./scripts/publicar.sh TU-USUARIO-DE-HUGGING-FACE"
  exit 1
fi

hf upload "$USUARIO/$SPACE" . . --repo-type space \
  --include "src/*" --include "web/*" --include "modelos/*" \
  --include "Dockerfile" --include "pyproject.toml" --include "uv.lock" --include "README.md" \
  --commit-message "Actualizar la app"

echo "Subido. Mira cómo se construye en https://huggingface.co/spaces/$USUARIO/$SPACE"
