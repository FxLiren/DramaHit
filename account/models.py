from django.db import models
from django.conf import settings


class ViewHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    script_id = models.IntegerField()

    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-viewed_at']

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'script_id'],
                name='unique_user_history_script'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.script_id}'