import smtplib

server = smtplib.SMTP('smtp.gmail.com', 587)

server.starttls()


server.login("#email", "")

msg = "Hello! This Message was sent by the help of Python"

server.sendmail("#Sender", "#Reciever", msg)
