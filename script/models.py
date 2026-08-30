from django.db import models

# Create your models here.

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