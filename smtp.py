  import smtplib
  from email.mime.multipart import MIMEMultipart
  from email.mime.text import MIMEText
  
  senderItems=['i-057778eda2f071c8e ==> aws-fs-kesava-01-rb-1', 'i-0189d6765094b9c83 ==> aws-fs-kesava-01-gz', 'i-0291bf04895773a8e ==> aws-fs-kesava-01-fm']
  
  mail_content = '''Hello,
  This is a simple mail. There is only text, no attachments are there The mail is sent using Python SMTP library.
  Thank You '''+'''\n'''+'\n'.join(map(str,senderItems))
  
  sender_address = '@gmail.com'
  sender_pass = ''
  receiver_address = '@gmail.com'
  message = MIMEMultipart()
  message['From'] = sender_address
  message['To'] = receiver_address
  message['Subject'] = 'Subject.'
  message.attach(MIMEText(mail_content, 'plain'))
  session = smtplib.SMTP('smtp.gmail.com', 587)
  session.starttls()
  session.login(sender_address, sender_pass)
  text = message.as_string()
  session.sendmail(sender_address, receiver_address, text)
  session.quit()
