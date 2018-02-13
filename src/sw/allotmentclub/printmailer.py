import pyramid_mailer.interfaces
import pyramid_mailer.mailer


class PrintMailer(pyramid_mailer.mailer.Mailer):
    """
    Dummy mailing instance, printing its mails to console.

    """
    def send(self, message):
        self._print(message)

    def send_immediately(self, message, fail_silently=False):
        self._print(message)

    def send_to_queue(self, message):
        self._print(message)

    def send_sendmail(self, message):
        self._print(message)

    def send_immediately_sendmail(self, message, fail_silently=False):
        self._print(message)

    def _print(self, message):
        if not message.sender:
            message.sender = '<no sender specified>'
        mime_message = message.to_message()
        print(mime_message)


def includeme(config):
    mailer = PrintMailer()
    config.registry.registerUtility(mailer, pyramid_mailer.interfaces.IMailer)
