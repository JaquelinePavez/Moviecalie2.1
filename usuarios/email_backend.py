# Importamos el backend de consola que Django utiliza
# para mostrar los correos electrónicos en la terminal.
from django.core.mail.backends.console import EmailBackend as ConsoleEmailBackend


# Creamos nuestro propio backend heredando del original de Django.
class EmailBackend(ConsoleEmailBackend):

    # Sobrescribimos el método encargado de mostrar cada correo.
    def write_message(self, message):

        # Obtenemos directamente el cuerpo del correo como texto,
        # evitando la codificación MIME que divide los enlaces largos.
        texto = message.body

        # Mostramos el contenido del correo en la consola.
        self.stream.write(texto)

        # Agregamos una línea separadora para distinguir
        # los diferentes correos enviados.
        self.stream.write("\n" + "-" * 60 + "\n")

        # Forzamos que el contenido se muestre inmediatamente
        # en la terminal, sin esperar a que se vacíe el búfer.
        self.stream.flush()