import pyramid_mailer.interfaces
import pyramid_mailer.mailer

from sw.allotmentclub.log import app_log


class LogMailer(pyramid_mailer.mailer.Mailer):
    """
    Mailer which logs sending/creating of messages
    """

    def _log(self, action, message):
        app_log.info(
            "{}: To: {} Subject: {}".format(
                action, ", ".join(message.recipients), message.subject
            )
        )

    def send(self, message):
        self._log("Mail sent", message)
        return super(LogMailer, self).send(message)

    def send_immediately(self, message, fail_silently=False):
        self._log("Mail sent immediately", message)
        return super(LogMailer, self).send_immediately(message, fail_silently)

    def send_to_queue(self, message):
        self._log("Mail added to queue", message)
        return super(LogMailer, self).send_to_queue(message)

    def send_sendmail(self, message):
        self._log("Mail sent via sendmail", message)
        return super(LogMailer, self).send_sendmail(message)

    def send_immediately_sendmail(self, message, fail_silently=False):
        self._log("Mail sent via sendmail immediately", message)
        return super(LogMailer, self).send_immediately_sendmail(
            message, fail_silently
        )


def includeme(config):
    settings = config.registry.settings
    prefix = settings.get("pyramid_mailer.prefix", "mail.")
    mailer = LogMailer.from_settings(settings, prefix)
    config.registry.registerUtility(mailer, pyramid_mailer.interfaces.IMailer)
