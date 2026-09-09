from django.db import models
from django.conf import settings


class ScriptMeta(models.Model):
    id = models.IntegerField(primary_key=True)
    script_name = models.TextField()
    image_url = models.TextField()
    script_type = models.TextField()
    players_count = models.TextField()
    play_time = models.TextField()
    rating = models.TextField()
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'combined_data'


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    script_id = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'script_id'],
                name='unique_user_script'
            )
        ]