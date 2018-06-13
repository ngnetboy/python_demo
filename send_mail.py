#coding=utf-8
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


class SendMail(object):
    def __init__(self, smtpserver, smtpport, smtpsender, smtppassword):
        self.smtpserver = smtpserver
        self.smtpport = smtpport
        self.smtpsender = smtpsender
        self.smtppassword = smtppassword
        self.smtp = None

    def login(self):
        try:
            self.smtp = smtplib.SMTP_SSL()
            self.smtp.connect(self.smtpserver, self.smtpport)
            self.smtp.login(self.smtpsender, self.smtppassword)
        except smtplib.SMTPAuthenticationError:
            return "SMTP authentication went wrong."
        except smtplib.SMTPException as e:
            return e.message
        return None

    def quit(self):
        self.smtp.quit()
        return None

    def send_email(self, receiver, msg):
        try:
            self.smtp.sendmail(self.smtpsender, receiver, msg.as_string())
        except SMTPRecipientsRefused:
            return "All recipients were refused"
        except SMTPSenderRefused:
            return "The server did not accept the from_addr."
        except smtplib.SMTPException as e:
            return e.message
        return None

    def send_mail_text(self, subject, body_text, receiver):
        if not self.smtp:
            ret = self.login()
            if ret:
                return ret
        #msg = MIMEText(body_text, "plain", "utf-8")
        msg = MIMEText(body_text, "html", "utf-8")
        msg['Subject'] = subject
        msg['From'] = self.smtpsender
        msg['To'] = receiver

        return self.send_email(receiver, msg)

    def send_mail_attachment(self, subject, body_text, receiver, file_path, file_name):
        if not self.smtp:
            ret = self.login()
            if ret:
                return ret
        
        msg = MIMEMultipart()
        msg.attach(MIMEText(body_text, "plain", "utf-8"))
        msg['Subject'] = subject
        msg['From'] = self.smtpsender
        msg['To'] = receiver

        att = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
        att["Content-Type"] = "application/octet-stream"
        att["Content-Disposition"] = "attachment; filename=%s" % file_name
        msg.attach(att)

        return self.send_email(receiver, msg)

    def send_mail_image(self, subject, body_text, receiver, file_path):
        if not self.smtp:
            ret = self.login()
            if ret:
                return ret

        msg = MIMEMultipart()
        msg.attach(MIMEText(body_text, "html", "utf-8"))
        msg['Subject'] = subject
        msg['From'] = self.smtpsender
        msg['To'] = receiver

        msgImage = MIMEImage(open(file_path, 'rb').read())
        # 定义图片 ID 在html文本中引用  <img src="cid:image1">
        msgImage.add_header('Content-ID', '<image1>')
        msg.attach(msgImage)

        return self.send_email(receiver, msg)

if __name__ == "__main__":
    sm = SendMail("xxx.xxx.com.cn", 465, "xxx@xxx.com.cn", "xxx") 

    meg_text = '''
    <h1>this is big title </h1>
    <a href=https://www.baidu.com>百度</a>
    <img src="cid:image1">
    '''
    meg = "test"
    #ret = sm.send_mail_text("test", meg_text, "ngnetboy@163.com")
    ret = sm.send_mail_attachment("test", meg_text, "ngnetboy@163.com", "smtp.jpg", "smtp.jpg")
    #ret = sm.send_mail_image("test", meg_text, "ngnetboy@163.com", "smtp.jpg")
    if ret:
        print ret

    sm.quit()

