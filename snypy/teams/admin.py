from django.contrib import admin


from .models import Team, UserTeam


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass


@admin.register(UserTeam)
class UserTeamAdmin(admin.ModelAdmin):
    pass
