from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Skill, UserSkill
# Register your models here.


class UserSkillInline(admin.TabularInline):
    model = UserSkill
    extra = 1
    autocomplete_fields = ('skill',)


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'surname', 'name', 'is_staff','is_active', 'date_joined')
    list_filter = ('is_staff','is_superuser', 'is_active', 'date_joined')
    list_display_links = ('email', 'surname')
    search_fields = ('email', 'name', 'surname')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {
            'fields': ('email', 'password'),
        }),
        ('Личная информация', {
            'fields': (
                'name',
                'surname',
                'avatar',
                'about',
                'phone',
                'github_url',
            ),
        }),
        ('Права', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        ('Даты', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'name',
                'surname',
                'password1',
                'password2',
            ),
        }),
    )

    inlines = (UserSkillInline,)


class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'created_at')
    list_filter = ('skill', 'created_at')
    search_fields = ('user__email', 'skill__name', 'user__surname')
    autocomplete_fields =('user', 'skill')
    ordering = ('-created_at',)


admin.site.register(User, UserAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(UserSkill, UserSkillAdmin)