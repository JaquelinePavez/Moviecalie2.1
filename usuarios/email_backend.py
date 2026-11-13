# Importamos el backend de consola que Django utiliza
# para mostrar los correos electrónicos en la terminal.
import django.core.mail.backends.console


# Creamos nuestro propio backend heredando del original de Django.
class EmailBackend(django.core.mail.backends.console.EmailBackend):

    def write_message(self, message):
        """
        Muestra el contenido del correo en la consola,
        agrega una separación entre los correos y actualiza
        la salida para que se vea todo inmediatamente.
        """

        texto = message.body
        self.stream.write(texto)

        # línea separadora para distinguir los diferentes correos
        self.stream.write("\n" + "-" * 60 + "\n")

        # Forzamos que el contenido se muestre inmediatamente
        # en la terminal, sin esperar a que se vacíe el búfer.
        self.stream.flush()
