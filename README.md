# 🏯 Sistema Experto de Planificación de Viajes a Japón

Sistema experto deductivo (*Forward Chaining*) desarrollado en Python con **Experta** y presentado mediante **Streamlit**.

## Contenido del Repositorio
* **`app.py`:** Interfaz web interactiva desarrollada con Streamlit.
* **`Japon_Sistema_Experto_Final_Oficial_V2.ipynb`:** Cuaderno Jupyter con la base de conocimiento completa (134 actividades) y las 25 reglas lógicas formalizadas.
* **`requirements.txt`:** Dependencias necesarias para ejecutar el proyecto (`streamlit`, `experta==1.9.4`, `fpdf2==2.7.9`).
* **`.gitignore`:** Filtro de exclusión de archivos temporales de Python y entornos virtuales.

## Taxonomía y Categorías Base
* **Visualizar (Perfiles en Interfaz):**
  * `Recreativa/Moderna`
  * `Gastronomia/Cultural`
  * `Explorador/Natural`
* **Categorías Base (Catálogo y Hechos):**
  * `Recreativa` (32 actividades)
  * `Gastronomia/Cultural` (83 actividades)
  * `Natural` (19 actividades)
  * **Total:** 134 actividades reales en 5 ciudades.

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
