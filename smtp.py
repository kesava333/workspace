from mailer import Mailer
from mailer import Message

message = Message(From="me@example.com",
                  To="you@example.com")
message.Subject = "An HTML Email"
message.Html = """<p>Hi!<br>
   DevOps <br>
  Hello</p>"""

sender = Mailer('smtp.example.com')
sender.send(message)
