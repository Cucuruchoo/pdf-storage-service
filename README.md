
# PDF Storage Service

## Descripción

Microservicio de almacenamiento de documentos PDF
desarrollado con Python, FastAPI y MongoDB.

Forma parte del proyecto Desarrollo de Software 2026.

## Responsabilidad

Persistir y administrar documentos mediante una
API REST interna utilizada por Request Service.

No realiza extracción de texto ni recibe el PDF original.

## Tecnologías

- Python 3.12
- FastAPI
- uv
- MongoDB
- PyMongo asíncrono
- Docker
- pytest
- Ruff

## Arquitectura

La aplicación separa sus responsabilidades en:

- API: endpoints y esquemas HTTP.
- Aplicación: casos de uso del CRUD.
- Dominio: modelo Document y repositorio abstracto.
- Infraestructura: persistencia mediante MongoDB.

La separación permite probar la lógica de negocio
sin depender directamente de MongoDB.

## Endpoints internos

- GET /health
- POST /internal/v1/documents
- GET /internal/v1/documents
- GET /internal/v1/documents/{document_id}
- PATCH /internal/v1/documents/{document_id}
- DELETE /internal/v1/documents/{document_id}

El endpoint POST recibe datos JSON que incluyen
el nombre del archivo, texto extraído, checksum
y tamaño del documento.

## Persistencia

Los documentos se almacenan en MongoDB.

Los datos principales incluyen:

- ID del documento.
- Nombre del archivo.
- Texto extraído.
- Checksum SHA-256.
- Tamaño del archivo.
- Fechas de creación y actualización.

## Prevención de duplicados

El sistema utiliza el checksum del documento
para detectar duplicados.

MongoDB incorpora un índice único sobre
el campo checksum.

El índice se crea automáticamente durante
el inicio del microservicio.

Cuando se intenta almacenar un documento
duplicado, la API devuelve HTTP 409 Conflict.

## Logging y trazabilidad

- Registros estructurados en JSON.
- Generación o conservación de X-Request-ID.
- Registro de estados HTTP y duración.
- Logs disponibles mediante Docker.

## Configuración

Variables de entorno:

- MONGO_URI
- MONGO_DATABASE
- MONGO_COLLECTION
- LOG_LEVEL

## Ejecución con Docker

Los tres repositorios deben estar ubicados
dentro de una misma carpeta.

Desde pdf-request-service ejecutar:

docker compose up --build -d

## Pruebas automatizadas

Desde pdf-storage-service:

uv sync

uv run pytest -q

uv run ruff check app tests

## Consideraciones

- Storage no extrae texto de los PDFs.
- MongoDB mantiene los datos mediante un volumen Docker.
- Los endpoints son internos.
- Request Service es la entrada pública de la aplicación.
