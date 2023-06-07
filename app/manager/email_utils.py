import smtplib
import config

from app.manager.log import log


class Email:
    def __init__(self):
        self.sender = config.SENDER
        self.receiver = config.RECEIVER
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.username = config.EMAIL_USERNAME
        self.password = config.EMAIL_PASSWORD

    def send_download_fail_mail(self, url):
        subject = "Cache-proxy file download fail"
        body = url
        message = f'Subject:{subject}\n\n{body}'
        try:
            server = smtplib.SMTP()
            server.connect(self.smtp_server, self.smtp_port)
            server.login(self.username, self.password)
            server.sendmail(self.sender, self.receiver, message)
            server.quit()
            log.info("Email sent successfully")
        except Exception as e:
            log.error(f"Error:{e}")


email = Email()
