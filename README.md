# 🏯 Sistema Experto de Planificación de Viajes a Japón

Sistema experto deductivo (*Forward Chaining*) desarrollado en Python(Versión 3.10) con **Experta** y presentado mediante **Streamlit**.                                                  
Grupo Proveedor: Grupo C -
Grupo Cliente: Grupo D

## Contenido del Repositorio
* **`app.py`:** Interfaz web interactiva desarrollada con Streamlit.
* **`Japon_Sistema_Experto_Final_Oficial_V2.ipynb`:** Cuaderno Jupyter con la base de conocimiento completa (134 actividades) y las 25 reglas lógicas formalizadas.
* **`requirements.txt`:** Dependencias necesarias para ejecutar el proyecto (`streamlit` y `experta==1.9.4`).
* **`.gitignore`:** Filtro de exclusión de archivos temporales de Python y entornos virtuales.

## Características
* **Catálogo Oficial:** 134 actividades turísticas reales en 5 ciudades (Tokio, Kioto, Osaka, Hiroshima y Nara).
* **Motor de Inferencia:** 25 reglas lógicas divididas en 5 fases (validación, filtrado por temporada y accesibilidad, ponderación de perfiles, hospedaje referencial y viabilidad presupuestaria con relajación de días).
* **Accesibilidad Exclusiva:** Evaluación directa del atributo booleano `accesibilidad`.
* **Hospedaje Referencial:** Deducción paralela de 3 opciones de alojamiento por ciudad (Económico, Estándar, Lujo) independientes del presupuesto de actividades.

## Instalación y Ejecución
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   cd TU_REPOSITORIO
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Iniciar la aplicación web:
   ```bash
   streamlit run app.py
   ```

Demo Online
👉 https://planificadordeviajesparajapon-grupoc.streamlit.app/

Aplicación de sistema experto para planificar viajes a Japón utilizando reglas de decisión, personalización de itinerarios y tecnologías Python + Streamli
