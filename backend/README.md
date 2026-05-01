# BinderJobs Backend - Motor de Búsqueda de Empleo

API backend para BinderJobs, un motor de búsqueda de empleo que agrega ofertas de múltiples fuentes de internet.

## Características

- **Búsqueda Multi-Fuente**: Busca en APIs de empleo, feeds RSS y portales web
- **Geolocalización Inteligente**: Prioriza ofertas según la ubicación del usuario
- **Ranking por Relevancia**: Ordena resultados por coincidencia con búsqueda y preferencias
- **Soporte Latinoamérica**: Fuentes específicas para Bolivia, Argentina, Chile, Perú, Colombia y México

## Fuentes de Datos

### APIs Gratuitas
- Arbeitnow
- Remotive  
- The Muse

### APIs con Key (Opcionales)
- JSearch (RapidAPI)
- Adzuna
- SerpAPI (Google Jobs)

### Feeds RSS
- RemoteOK
- WeWorkRemotely
- Jobicy
- Tecnoempleo

### Portales Latinoamericanos (Scraping)
- CompuTrabajo (Bolivia, Argentina, Chile, Perú, Colombia, México)
- Trabajo.bo
- Bumeran
- OCC Mundial
- Y más...

## Instalación

```bash
cd backend
pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Búsqueda Principal
```
GET /jobs/search?q=desarrollador&country=Bolivia&city=Tarija
```

Parámetros:
- `q`: Término de búsqueda (cargo, empresa, habilidad)
- `country`: País del usuario
- `city`: Ciudad del usuario
- `state`: Departamento/Estado
- `modality`: Remoto, Presencial, Híbrido
- `salary_min`: Salario mínimo deseado
- `limit`: Máximo de resultados (default: 100)

### Búsqueda Cercana
```
GET /jobs/nearby?city=Tarija&country=Bolivia
```

Prioriza ofertas de la misma ciudad y departamento.

### Búsqueda Avanzada (POST)
```
POST /jobs/search
Content-Type: application/json

{
    "query": "programador",
    "country": "Bolivia",
    "city": "Tarija",
    "state": "Tarija",
    "modality": "Remoto",
    "salary_min": 5000,
    "limit": 50
}
```

### Búsqueda en Segundo Plano
```
POST /background/search
```

Endpoint optimizado para el WorkManager de Android.

### Información de Fuentes
```
GET /sources
GET /sources/by-country/Bolivia
```

### Ciudades de Bolivia
```
GET /location/bolivia/cities
```

## Configuración de API Keys (Opcional)

Para habilitar fuentes premium, configura las siguientes variables de entorno:

```bash
export RAPIDAPI_KEY=tu_api_key_de_rapidapi
export ADZUNA_API_KEY=tu_api_key_de_adzuna
export SERPAPI_KEY=tu_api_key_de_serpapi
```

## Sistema de Ranking

El ranking considera:
1. **Relevancia de búsqueda** (45%): Coincidencia con el término de búsqueda
2. **Ubicación** (40%): Prioridad a ofertas de la misma ciudad/departamento
3. **Preferencias** (15%): Modalidad y salario preferidos

### Prioridad de Ubicación (Bolivia)
- Misma ciudad: Score máximo
- Mismo departamento: Score alto
- Mismo país: Score medio
- Remoto/Global: Score base

## Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Ejecutar en modo desarrollo
uvicorn app.main:app --reload

# Ver documentación de la API
# http://localhost:8000/docs
```
