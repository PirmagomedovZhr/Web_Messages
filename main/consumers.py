# main/consumers.py

import imaplib
import email
from email.header import decode_header
import json
from channels.generic.websocket import WebsocketConsumer

class MessageConsumer(WebsocketConsumer):
    def connect(self):
        print('WebSocket connection established')
        self.accept()

    def disconnect(self, close_code):
        print(f'WebSocket connection closed with code: {close_code}')

    def receive(self, text_data):
        print('Received data from WebSocket')
        imap_host = 'imap.mail.ru'
        imap_port = 993
        email_address = ''
        password = ''

        imap_server = imaplib.IMAP4_SSL(imap_host, imap_port)

        try:
            print(f'Trying to login with email: {email_address}')
            imap_server.login(email_address, password)
            print('IMAP login successful!')

            imap_server.select("inbox")
            print('Connected to inbox')

            status, messages = imap_server.search(None, 'ALL')
            if status != 'OK':
                print('Error searching inbox.')
                return

            mail_ids = messages[0].split()
            print(f'Total messages: {len(mail_ids)}')
            email_messages = []

            for mail_id in mail_ids[-10:]:  # Получаем последние 10 писем
                print(f'Fetching mail ID: {mail_id}')
                status, msg_data = imap_server.fetch(mail_id, '(RFC822)')
                if status != 'OK':
                    print(f'Error fetching mail ID {mail_id}')
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        from_ = msg.get("From")
                        date_ = msg.get("Date")
                        message_body = ""
                        attachments = []

                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                try:
                                    body = part.get_payload(decode=True).decode()
                                except:
                                    body = ""

                                if "attachment" in content_disposition:
                                    filename = part.get_filename()
                                    if filename:
                                        attachments.append(filename)
                                else:
                                    if content_type == "text/plain":
                                        message_body = body

                        else:
                            message_body = msg.get_payload(decode=True).decode()




                        email_messages.append({
                            "subject": subject,
                            "from": from_,
                            "date": date_,
                            "text": message_body,
                            "attachments": attachments,
                        })

            # Отправляем сообщения клиенту
            self.send(text_data=json.dumps({
                "type": "email_messages",
                "messages": email_messages
            }))

            imap_server.logout()
        except imaplib.IMAP4.error as e:
            print(f'IMAP login error: {e}')
            self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))
        except Exception as e:
            print(f'Unexpected error: {e}')
            self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))
