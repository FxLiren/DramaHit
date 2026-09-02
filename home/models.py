from django.db import models

class Script(models.Model):
    # 對應截圖中的所有欄位
    script_name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image_url = models.TextField(null=True, blank=True)
    script_type = models.TextField(null=True, blank=True)
    players_count = models.TextField(null=True, blank=True)
    play_time = models.TextField(null=True, blank=True)
    rating = models.TextField(null=True, blank=True)
    shop_name = models.TextField(null=True, blank=True)
    official_site = models.TextField(null=True, blank=True)
    ig_url = models.TextField(null=True, blank=True)
    fb_url = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'combined_data'  # 指定讀取這張資料表
        managed = False             # 不由 Django 自動管理/修改表結構