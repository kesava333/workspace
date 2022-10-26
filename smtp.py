import smtplib
host = "smtp.clearpath.ai"
server = smtplib.SMTP(host)
msg = "Hello! This Message is to test deadman switch"
server.sendmail("bundles-noreply@clearpath.ai", "kginjupalli@clearpath.ai", msg)
server.quit()
