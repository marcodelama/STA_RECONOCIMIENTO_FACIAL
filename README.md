# Requisitos
pip, python 3.8, acceso a mesa16 (DB)


# Ejecutar archivo requirements.txt para instalar dependencias
pip install -r requirments.txt

# Generar entorno venv para ejecutar el proyecto
python -m venv venv

# Ingresar al entorno
venv/Scripts/activate

# Iniciar servidor dentro del entorno virtual
python manage.py runserver (puerto_disponible)