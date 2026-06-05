# Checklist Service

**Checklist Service** es un microservicio fundamental del ecosistema diseñado para digitalizar y gestionar el ciclo de vida de las **inspecciones vehiculares**. Su objetivo es permitir la configuración de plantillas (templates) de verificación, procesar inspecciones en tiempo real para diversos tipos de vehículos (motos, livianos y pesados) y capturar parámetros de seguridad crudos como el labrado (desgaste) geométrico de los neumáticos.

Este servicio es completamente "Agnóstico a Estados", construido estrictamente empleando patrones de **Arquitectura Hexagonal (Ports and Adapters)** y **Domain-Driven Design (DDD)**. Garantiza que la lógica pura del negocio (Dominio) no esté acoplada a la web, frameworks de base de datos ni flujos de comunicación con otros microservicios.

## 🚀 Funcionalidades Principales

El proyecto se divide internamente en 3 "Bounded Contexts" de negocio:
1. **Templates (Plantillas):** Configuración paramétrica y jerárquica (Secciones > Subsecciones > Ítems) que dictan qué se le inspeccionará a un vehículo tomando en cuenta su tipo (e.g. Motocicleta vs Pesado).
2. **Inspecciones (Core):** Maneja el inicio, ejecución parcial (Draft/En Progreso) y cierre de la inspección. Incluye reglas de dominio estrictas para confirmar que el checklist y el labrado estén debidamente guardados antes de emitir un veredicto definitivo.
3. **Labrado (Measurement):** Un submódulo especializado para ingerir, validar y retener los niveles de milímetros (mm) de desgaste geométrico en el esquema `Eje -> Rueda -> Llanta`. 

## 🏗️ Arquitectura y Tecnologías
La arquitectura separa el código en capas: `domain/` (Capa Pura), `application/` (Casos de Uso) y `adapters/` (Driving: DRF Inbound y Driven: Mappers a MongoEngine/Pika RabbitMQ).

**Stack Tecnológico y Versiones:**
- **Python**: 3.12+
- **Django**: 6.0.3 _(Base de abstracción y Servidor)_
- **Django REST Framework (DRF)**: 3.17.1 _(Capa Driving / Endpoints Inbound)_
- **MongoDB**: PyMongo 4.16.0 y MongoEngine 0.29.3 _(Persistencia Documental en Capa Driven)_
- **RabbitMQ**: Pika 1.3.2 _(Comunicación RPC RPC entre microservicios clientes/vehículos)_
- **Autenticación**: Cabecera Estática M2M (`X-API-KEY`) delegada desde API Gateways.

---

## 🛠️ Prerequisitos para Desarrollo

Antes de instalar este entorno debes contar instalado en tu máquina con:
*   **Python:** Versión `3.12.x` o superior.
*   **MongoDB:** Un servidor de MongoDB corriendo de forma local o en la nube (ej. MongoDB Atlas).
*   **RabbitMQ:** (Requerido para funcionalidades completas de RPC) corriendo de forma local o a través de Docker.

---

## 💻 Guía Rápida de Instalación y Ejecución

Sigue estos pasos para arrancar el servidor en local:

### 1. Clonar el proyecto
```bash
git clone https://github.com/CDA-SYSTEM/checklist-service.git
cd checklist-service
```

### 2. Configurar el Entorno Virtual de Python
Aísla las dependencias creando y activando un entorno virtual:
```bash
# En Windows (Powershell)
python -m venv env
.\env\Scripts\Activate.ps1

# En Linux/Mac
python3 -m venv env
source env/bin/activate
```

### 3. Instalar las dependencias
Con el entorno activado, instala todo el stack del `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configurar las Variables de Entorno
En la raíz existe el archivo `.env.example`. Cópialo y renómbralo a `.env`:
```bash
cp .env.example .env
```
Luego **edita tu archivo `.env`** agregando tus credenciales de entorno. Es valioso indicar al menos:
- `MONGO_HOST`, `MONGO_PORT`, `MONGO_DB_NAME`
- `API_SECRET_KEY` (Token personal de prueba para el Postman)
- `RABBITMQ_URI` (Si careces de RabbitMQ, dejar en blanco simulará un "Bypass" saltando dependencias).

### 5. Iniciar el Servidor de Desarrollo
```bash
python manage.py runserver
```
Por defecto, la aplicación comenzará a correr en [`http://127.0.0.1:8000`](http://127.0.0.1:8000).

---
