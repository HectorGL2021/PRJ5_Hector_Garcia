# PRJ5 — Backend API con CI/CD y Despliegue en Azure

Aplicación backend REST API desarrollada con **Flask** y **PostgreSQL**, contenerizada con **Docker Compose**, automatizada con **GitHub Actions** CI/CD, y desplegada en **Azure Container Apps**.

**Autor:** Hector Garcia  
**Asignatura:** UNIR — Entregable 5

---

## 📐 Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Actions                           │
│  ┌──────┐   ┌──────┐   ┌────────────┐   ┌──────────────────┐   │
│  │ Test │──▶│Build │──▶│ Push a ACR  │──▶│ Deploy Azure CA  │   │
│  └──────┘   └──────┘   └────────────┘   └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Azure Container Apps │
                    │  ┌─────────────────┐  │
                    │  │  Flask Backend   │  │
                    │  │  (Puerto 5000)   │  │
                    │  └────────┬────────┘  │
                    │           │            │
                    │  ┌────────▼────────┐  │
                    │  │   PostgreSQL    │  │
                    │  │   (Puerto 5432) │  │
                    │  └─────────────────┘  │
                    └───────────────────────┘
```

---

## 🛠️ Requisitos Previos

- [Python 3.11+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Azure CLI](https://learn.microsoft.com/es-es/cli/azure/install-azure-cli)
- Cuenta de [GitHub](https://github.com/) y [Azure](https://portal.azure.com/)

---

## 🚀 Ejecución Local

### Con Docker Compose (recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/<tu-usuario>/PRJ5_Hector_Garcia.git
cd PRJ5_Hector_Garcia

# Levantar servicios (backend + PostgreSQL)
docker-compose up --build

# Verificar en http://localhost:5000
```

### Sin Docker (solo desarrollo)

```bash
pip install -r requirements.txt
export DB_HOST=localhost  # o la IP de tu PostgreSQL
python app.py
```

---

## 📡 Endpoints de la API

| Método   | Ruta          | Descripción                    |
| -------- | ------------- | ------------------------------ |
| `GET`    | `/`           | Información de la API          |
| `GET`    | `/health`     | Health check + estado de la BD |
| `GET`    | `/items`      | Listar todos los ítems         |
| `POST`   | `/items`      | Crear un nuevo ítem            |
| `GET`    | `/items/<id>` | Obtener un ítem por ID         |
| `DELETE` | `/items/<id>` | Eliminar un ítem               |

### Ejemplos de uso

```bash
# Info de la API
curl http://localhost:5000/

# Health check
curl http://localhost:5000/health

# Crear un ítem
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Mi item", "description": "Descripción del item"}'

# Listar ítems
curl http://localhost:5000/items

# Obtener ítem por ID
curl http://localhost:5000/items/1

# Eliminar ítem
curl -X DELETE http://localhost:5000/items/1
```

---

## 🧪 Tests

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests unitarios
pytest test_app.py -v
```

Los tests usan **SQLite en memoria** (no requieren PostgreSQL).

---

## ☁️ Configuración de Azure

### 1. Crear Azure Container Registry (ACR)

```bash
# Crear grupo de recursos
az group create --name rg-prj5 --location westeurope

# Crear ACR
az acr create --name prj5hectorgarcia --resource-group rg-prj5 --sku Basic --admin-enabled true

# Obtener credenciales del ACR
az acr credential show --name prj5hectorgarcia
```

### 2. Subir imagen manualmente (opcional)

```bash
az acr login --name prj5hectorgarcia
docker tag prj5-backend:latest prj5hectorgarcia.azurecr.io/prj5-backend:v1
docker push prj5hectorgarcia.azurecr.io/prj5-backend:v1
```

### 3. Crear Azure Container App

```bash
# Crear entorno de Container Apps
az containerapp env create \
  --name prj5-env \
  --resource-group rg-prj5 \
  --location westeurope

# Desplegar la aplicación
az containerapp create \
  --name prj5-backend \
  --resource-group rg-prj5 \
  --environment prj5-env \
  --image prj5hectorgarcia.azurecr.io/prj5-backend:latest \
  --registry-server prj5hectorgarcia.azurecr.io \
  --registry-username <ACR_USERNAME> \
  --registry-password <ACR_PASSWORD> \
  --target-port 5000 \
  --ingress external \
  --env-vars DB_HOST=<db-host> DB_PORT=5432 DB_NAME=appdb DB_USER=appuser DB_PASSWORD=apppassword123
```

### 4. Crear Service Principal para CI/CD

```bash
az ad sp create-for-rbac --name "github-actions-prj5" \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/rg-prj5 \
  --json-auth
```

Copiar el JSON de salida como secreto `AZURE_CREDENTIALS` en GitHub.

---

## 🔄 Pipeline CI/CD (GitHub Actions)

El pipeline se ejecuta en cada push a `main`:

```
Test (pytest) → Build (Docker) → Push (ACR) → Deploy (Azure Container Apps)
```

### Secretos necesarios en GitHub

Ir a **Settings** → **Secrets and variables** → **Actions** y añadir:

| Secreto                   | Descripción                   |
| ------------------------- | ----------------------------- |
| `AZURE_CREDENTIALS`       | JSON del Service Principal    |
| `ACR_LOGIN_SERVER`        | `prj5hectorgarcia.azurecr.io` |
| `ACR_USERNAME`            | Usuario admin del ACR         |
| `ACR_PASSWORD`            | Contraseña admin del ACR      |
| `AZURE_RESOURCE_GROUP`    | `rg-prj5`                     |
| `AZURE_CONTAINERAPP_NAME` | `prj5-backend`                |

---

## 📊 Monitoreo y Validación

```bash
# Ver logs de la aplicación
az containerapp logs show --name prj5-backend --resource-group rg-prj5

# Ver estado del Container App
az containerapp show --name prj5-backend --resource-group rg-prj5 --query "properties.runningStatus"

# Verificar la URL pública
az containerapp show --name prj5-backend --resource-group rg-prj5 --query "properties.configuration.ingress.fqdn" -o tsv
```

---

## 📁 Estructura del Proyecto

```
PRJ5_Hector_Garcia/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # Pipeline CI/CD
├── app.py                     # Aplicación Flask (API REST)
├── config.py                  # Configuración (BD, entorno)
├── models.py                  # Modelo Item (SQLAlchemy)
├── test_app.py                # Tests unitarios (pytest)
├── requirements.txt           # Dependencias Python
├── Dockerfile                 # Imagen del contenedor
├── docker-compose.yml         # Orquestación de servicios
├── .env                       # Variables de entorno (local)
├── .dockerignore              # Exclusiones Docker
├── .gitignore                 # Exclusiones Git
└── README.md                  # Este archivo
```

---

## 📄 Licencia

Proyecto académico — UNIR 2026
