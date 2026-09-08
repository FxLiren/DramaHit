from django.db import models


class Review(models.Model):
    script_id = models.IntegerField()
    nickname = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nickname} - Script {self.script_id}"