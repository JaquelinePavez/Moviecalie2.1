# Moviecalie2.1
es una aplicación web enfocada en la industria cinematográfica. Desarrollada inicialmente durante la cursada de *Programación Web I*, el proyecto entra en una nueva etapa en *Programación Web II* para evolucionar hacia un entorno dinámico, seguro y escalable impulsado por el framework **Django**.


# GUÍA PASO A PASO PARA UNIRSE AL PROYECTO
¡Hola equipo! Ya dejé el proyecto configurado en la nube con GitHub Codespaces. 
Esto significa que no necesitan instalar nada en sus computadoras (ni Python, ni extensiones, ni entornos virtuales). 
Todo va a correr idéntico en la nube.

Sigan estos pasos en orden para empezar a trabajar:

1️⃣ Aceptar la invitaciónRevisen su correo electrónico (el asociado a GitHub) o entren directo a las notificaciones de su cuenta en GitHub.Busquen la invitación para colaborar en el repositorio y hagan clic en Accept invitation.

2️⃣ Crear tu entorno (Codespace)
Una vez adentro del repositorio en GitHub, hagan clic en el botón verde 🟢 Code (arriba a la derecha).
Seleccionen la pestaña Codespaces.Hagan clic en el botón verde Create codespace on main.Esperen unos 2 minutos. La pantalla va a cargar un VS Code en el navegador. De fondo, el sistema va a instalar automáticamente Python, las extensiones de Django, las librerías del proyecto y va a preparar la base de datos. No toquen nada hasta que se abra la terminal abajo.

3️⃣ Probar el proyecto Django
Cuando la terminal termine de cargarse sola abajo, escriban el siguiente comando para encender el servidor:

python manage.py runserver

Abajo a la derecha les va a aparecer un cartel flotante de VS Code que dice "Open in Browser" (Abrir en el navegador). 
Hagan clic ahí.Se va a abrir una pestaña nueva donde van a poder ver y probar la página web (HTML/CSS/Django) en tiempo real.


🛠️ CÓMO TRABAJAR EN EQUIPO TODOS LOS DÍAS 
(Comandos Git)

Para que no nos pisemos el código ni tengamos conflictos con la base de datos, usemos siempre estos comandos en la terminal del Codespace:
SIEMPRE antes de empezar a programar 

Para descargar lo que hizo el resto):

git pull origin main

(Si alguien creó tablas nuevas, después de hacer el pull ejecuten python manage.py migrate para actualizar su base de datos local).

Cuando terminen de programar algo y quieran guardarlo en GitHub:

git add .
git commit -m "Explicación breve de lo que cambiaste o agregaste"
git push origin main


Si instalan una librería nueva (ej: pillow, djangorestframework, etc):

Avisen al grupo, ejecuten pip freeze > requirements.txt y suban ese archivo a GitHub con los comandos de arriba para que los demás también la tengan.