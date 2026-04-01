from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0017_post_video"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="fb_comments",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="post",
            name="fb_likes",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="post",
            name="fb_shares",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="post",
            name="ig_comments",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="post",
            name="ig_likes",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="post",
            name="ig_shares",
            field=models.CharField(default="NA", max_length=20),
        ),
        migrations.AddField(
            model_name="post",
            name="li_comments",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="post",
            name="li_likes",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="post",
            name="li_shares",
            field=models.IntegerField(default=0),
        ),
    ]
