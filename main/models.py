from django.db import models

class EmailMessage(models.Model):
    subject = models.CharField(max_length=255)
    sent_date = models.DateTimeField()
    received_date = models.DateTimeField()
    message_body = models.TextField()
    attachments = models.JSONField(default=list)  # Можно использовать JSONField для хранения списка прикреплённых файлов

    def __str__(self):
        return self.subject
