from django.contrib import admin

# Register your models here.
from .models import Antispam, BanAppeal, Ban, Board, Cite, Flood, IpNote, Modlog, Mod, Mute, News, Noticeboard, Pm, Post, Report, Robot, SearchQuerie, ThemeSetting

admin.site.register(Antispam)
admin.site.register(BanAppeal)
admin.site.register(Ban)
admin.site.register(Board)
admin.site.register(Cite)
admin.site.register(Flood)
admin.site.register(IpNote)
admin.site.register(Modlog)
admin.site.register(Mod)
admin.site.register(Mute)
admin.site.register(News)
admin.site.register(Noticeboard)
admin.site.register(Pm)
admin.site.register(Report)
admin.site.register(Robot)
admin.site.register(SearchQuerie)
admin.site.register(ThemeSetting)
