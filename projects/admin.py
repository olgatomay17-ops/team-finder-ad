from django.contrib import admin
from .models import Project, ProjectMembership


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 1
    autocomplete_fields = ('user',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'owner__email', 'owner__name', 'owner__surname')
    autocomplete_fields = ('owner',)
    inlines = (ProjectMembershipInline,)


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'joined_at')
    list_filter = ('project', 'joined_at')
    autocomplete_fields = ('user', 'project')
