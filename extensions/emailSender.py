import smtplib

from email.mime.text import MIMEText


class EmailSender:

    def __init__(self):
        self.id = '20142921.sw.cau@gmail.com'
        self.password = 'fwihxqfexfnxpaek'
        self.sender = 'noreply.capstone.deal@gmail.com'
        self.title = '[DEAL] 이메일을 재설정해주세요.'

        self.smtp_url = 'smtp.gmail.com'
        self.smtp_port = 587
        self.smtp = smtplib.SMTP(host=self.smtp_url, port=self.smtp_port)

        self.template = MIMEText('')

        self._init()

    def _init(self):
        self.smtp.starttls()
        self.smtp.login(self.id, self.password)

    def _generate_dynamic_link(self):
        return 'aaa'

    def _make_form(self):
        return '여기로 가세요 : %s' % self._generate_dynamic_link()

    def send(self, email):
        self.template = MIMEText(self._make_form())
        self.template['Subject'] = self.title
        self.template['From'] = self.sender
        self.template['To'] = email
        self.smtp.sendmail(from_addr=self.sender, to_addrs=email, msg=self.template.as_string())

    def __del__(self):
        self.smtp.quit()
