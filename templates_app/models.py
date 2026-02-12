import re

from django.conf import settings
from django.db import models


class MasterTemplate(models.Model):
    """Master table: stores template strings with {{variable}} placeholders."""

    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True, default="")
    body = models.TextField(help_text="Use {{variable_name}} for placeholders.")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="templates",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name

    def extract_variable_names(self):
        """Extract all {{variable}} names from subject and body."""
        pattern = r"\{\{(\w+)\}\}"
        names = set(re.findall(pattern, self.subject))
        names |= set(re.findall(pattern, self.body))
        return sorted(names)

    def sync_variables(self):
        """Create Variable and TemplateVariable entries for all placeholders."""
        var_names = self.extract_variable_names()
        for name in var_names:
            variable, _ = Variable.objects.get_or_create(name=name)
            TemplateVariable.objects.get_or_create(
                template=self, variable=variable
            )
        # Remove stale links
        self.templatevariable_set.exclude(
            variable__name__in=var_names
        ).delete()

    def render(self, values: dict) -> tuple[str, str]:
        """Render subject and body by replacing {{var}} with provided values."""
        subject = self.subject
        body = self.body
        for key, val in values.items():
            placeholder = "{{" + key + "}}"
            subject = subject.replace(placeholder, val)
            body = body.replace(placeholder, val)
        return subject, body


class Variable(models.Model):
    """Object table: stores individual variable definitions."""

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TemplateVariable(models.Model):
    """Merge/Join table: connects MasterTemplate to Variable."""

    template = models.ForeignKey(MasterTemplate, on_delete=models.CASCADE)
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("template", "variable")
        ordering = ["variable__name"]

    def __str__(self):
        return f"{self.template.name} -> {self.variable.name}"
