# Backend-Django-Python-
Pequeño servicio web desarrollado con Django and Python.  
Recibe un token de sesión de LinkedIn ('li_at') a través de una solicitud POST y, utilizando el actor 'linkedin-jobs-scraper' de Apify, devuelve una lista de ofertas laborales en formato JSON.  


Este servicio web está diseñado para manejar posibles errores como tokens invàlidos, problemas de red o timeouts, respondiendo como corresponde en cada caso.  

## Estructura del Proyecto
```
linkedin_scraper_project/  
|-- venv/ #Entorno virtual con dependencias  
|-- linkedin_scraper_project/ # Configuracion principal de Django  
|   |-- settings.py  
|   |-- urls.py  
|   |-- asgi.py  
|   |-- wsgi.py  
|   |-- __init__.py  
|-- jobs_api/ #Aplicacion Djando para lógica del servicio REST  
|   |-- migrations/  
|   |-- views.py  
|   |-- admin.py  
|   |-- urls.py  
|   |-- models.py  
|   |-- test.py  
|   |-- __init__.py  
|-- .env #Archivo para variables de entorno (APIFY_API_TOKEN)  
|-- manage.py # Línea de comandos de Django  
|-- README.md # Este archivo  
|__ requirements.txt # Dependencias del proyecto
```


## Requisitos previos
**Python 3.8.+**  
**pip** (gestor de paquetes de Python)  
**git** (para clonar el repositorio)  


## Cómo correr el proyecto
1. **Clonar el repositorio**  
[gitclone](https://github.com/MilagrosToyos/Backend-Django-Python-.git)

2. **Crear y Activar el entorno Virtual**  
    python3 -m venv venv  
    source venv/bin/activate  
(una vez activado, deberías ver (venv) al inicio de tu prompt)

3. **Instalar las dependencias**  
pip install -r requirements.txt   
(el archivo txt ya tiene todas las dependencias que se necesitan instalar en el entorno virtual)  

4. **Configurar variables de Entorno (`.env`)**
Crea un archivo con el nombre `.env` en la raíz del proyecto e insertar la línea   
APYFY_API_TOKEN="you_API_Token_here"  

5. **Configurar li_at en `views.py` para la vista HTML**  
      En `show_works_html(request)` modificar la línea `json={"li_at": "your_li_at_token_LinkedIn"},`
6. **Ejecutar Migraciones de Django**  
python manage.py migrate  

7. **Iniciar el Servidor de Desarrollo de Django**  
python manage.py runserver  
y deja esta terminal abierta.  

8. **Probar el Endpoint REST**  
Con el servidor corriendo, en otra ventana de la terminal en la raiz del proyecto también, podés probar el endpoint de la siguiente forma:  
8-1. **Activa el entorno virtual **  
source venv/bin/activate  
8-2. ** Ejecuta el siguiente comando `curl`**  
```
curl -X POST \
  http://127.0.0.1:8000/api/linkedin-jobs/ \
  -H 'Content-Type: application/json' \
  -d '{
        "li_at": "you_li_at_token_LinkedIn"
      }'
  ```

  
**Respuesta esperada (Éxito)**  
Además del Endpoint API que devuelve los trabajos en formato JSON, es posible visualizar los resultados mediante una **vista HTML responsiva** que muestra las ofertas de trabajo en tarjetas estilizadas con Bootstrap 4.4  
Ruta del navegador:  
`http://localhost:8000/api/linkedin-jobs/html/`   


### Mejoras futuras / consideraciones
1. **Persistencia de datos:**  
Los resultados de las ofertas laborales podrían guardarse en alguna base de datos, para poder consultar los datos sin tener que llamar a Apify repetidas veces.  
2. **Seguridad:**  
Proteger el endpoint `POST /api/linkedin-jobs/` con un sistema de autenticación para que solo los usuarios autorizados puedan consumir el servicio.  
3. **Dockerización:**  
Crear un `Dockerfile` para facilitar el empaquetado y despliegue del servicio en cualquier entorno.
4. **Manejo de errores detallado:**  
A cada tipo de error, devolver un mensaje que especifique el tipo de error al llamar a Apify, ya sea timeout, li_at inválido, HTTPError, error de red, etc. que se abarcan como un "todo" en un solo RequestException.  
      
