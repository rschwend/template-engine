from django.contrib import admin

from .models import MasterTemplate, TemplateVariable, Variable


class TemplateVariableInline(admin.TabularInline):
    model = TemplateVariable
    extra = 0


@admin.register(MasterTemplate)
class MasterTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "created_by", "updated_at")
    inlines = [TemplateVariableInline]


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(TemplateVariable)
class TemplateVariableAdmin(admin.ModelAdmin):
    list_display = ("template", "variable")
