import django.db.models.deletion
import tinymce.models
from django.conf import settings
from django.db import migrations, models

import todianedev.storage


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="HostedTool",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, help_text="Used in the public URL: /tools/<slug>/ . Leave blank to auto-fill from the title.", max_length=200, unique=True)),
                ("description", tinymce.models.HTMLField(blank=True, help_text="Optional short caption shown above the tool on its public page.")),
                ("link_text", models.CharField(blank=True, help_text="Optional. The clickable label for a link button shown at the top AND bottom of the tool's page (e.g. 'Back to the shop', 'Get the full guide'). Leave blank to hide the link.", max_length=120, verbose_name="URL name")),
                ("link_url", models.URLField(blank=True, help_text="Where the link button points. Only shown if both fields are filled.", max_length=500, verbose_name="URL link")),
                ("link_position", models.CharField(choices=[("both", "Top and bottom (default)"), ("top", "Top only"), ("bottom", "Bottom only")], default="both", help_text="Where the link button appears on the page, if it's set.", max_length=10, verbose_name="URL link position")),
                ("more_info_title", models.CharField(blank=True, help_text="Optional heading for an extra block of text shown at the end of the page, below the tool. Handy for background, instructions, or context you don't want cluttering the top of the page — and the extra real text also helps this page get found in search.", max_length=200, verbose_name="Extra title")),
                ("more_info_description", tinymce.models.HTMLField(blank=True, help_text="Optional. Shown under the extra title, at the end of the page.", verbose_name="Extra description")),
                ("html_file", models.FileField(help_text="Upload the single .html file. Hit save and it goes live at the URL above.", storage=todianedev.storage.SecureStorage(), upload_to="tools/")),
                ("image", models.ImageField(blank=True, help_text="Optional small thumbnail shown on the /tools/ list page. Max 1MB, 1200x1200px or smaller. Leave blank to show a plain card with no image.", null=True, storage=todianedev.storage.PublicStorage(), upload_to="tools/cards/")),
                ("published", models.BooleanField(default=True, help_text="Untick to take the tool offline without deleting it.")),
                ("allow_saving", models.BooleanField(default=True, help_text="When ticked, a logged-in visitor can save what they typed in this tool to their own dashboard, and come back to it later. Turning this off is not recommended for a tool that produces something worth keeping (a list, a plan, a compass statement) — most visitors expect to be able to find it again.", verbose_name="Let visitors save their results")),
                ("access", models.CharField(choices=[("free", "Free — anyone can use it"), ("paid", "Paid — only buyers can use it")], default="free", help_text="Free tools count toward your hosted-tool limit. Paid tools do not count, and are unlocked only by buying a linked shop product.", max_length=10)),
                ("order", models.PositiveIntegerField(db_index=True, default=0, help_text="Lower numbers appear first on the /tools/ list. Tools with the same number fall back to alphabetical order.")),
                ("marketing_list_id", models.CharField(blank=True, help_text="Optional. Reserved for a connected email marketing platform: when someone signs up from THIS tool's newsletter box, they would be added to this list/group ID instead of the store's default list. Leave blank to use the default.", max_length=100, verbose_name="Marketing list ID")),
                ("marketing_tag", models.CharField(blank=True, help_text="Optional. Reserved for a connected email marketing platform: a tag applied to people who sign up from THIS tool, so you can segment them later. Leave blank for no extra tag.", max_length=100, verbose_name="Marketing tag")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Hosted Tool",
                "verbose_name_plural": "Hosted Tools",
                "ordering": ["order", "title"],
            },
        ),
        migrations.CreateModel(
            name="SavedToolResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tool_title", models.CharField(blank=True, max_length=200)),
                ("tool_slug", models.SlugField(blank=True, max_length=200)),
                ("label", models.CharField(help_text="Short name the visitor sees on their dashboard, e.g. 'My top 3 values'.", max_length=300)),
                ("data", models.JSONField(blank=True, default=dict, help_text="Structured payload from a cooperating tool, if any.")),
                ("results_html", models.TextField(blank=True, help_text="Sanitised HTML snapshot of the tool's output at save time.")),
                ("results_text", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("tool", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="saved_results", to="tools.hostedtool")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="saved_tool_results", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Saved tool result",
                "ordering": ["-created"],
            },
        ),
        migrations.AddIndex(
            model_name="savedtoolresult",
            index=models.Index(fields=["user", "tool", "-created"], name="tools_str_user_tool_idx"),
        ),
    ]
