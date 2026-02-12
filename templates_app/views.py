import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MasterTemplateForm, SignUpForm
from .models import MasterTemplate


def landing_page(request):
    if request.user.is_authenticated:
        return redirect("template_list")
    return render(request, "landing.html")


def signup_view(request):
    if not settings.SIGNUP_ENABLED:
        messages.error(request, "Die Registrierung ist derzeit deaktiviert.")
        return redirect("landing")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registrierung erfolgreich!")
            return redirect("template_list")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def template_list(request):
    templates = MasterTemplate.objects.filter(created_by=request.user)
    return render(request, "templates_app/template_list.html", {"templates": templates})


@login_required
def template_create(request):
    if request.method == "POST":
        form = MasterTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            template.sync_variables()
            messages.success(request, "Template erstellt.")
            return redirect("template_list")
    else:
        form = MasterTemplateForm()
    return render(request, "templates_app/template_form.html", {
        "form": form,
        "title": "Neues Template",
    })


@login_required
def template_edit(request, pk):
    template = get_object_or_404(MasterTemplate, pk=pk, created_by=request.user)
    if request.method == "POST":
        form = MasterTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            template.sync_variables()
            messages.success(request, "Template aktualisiert.")
            return redirect("template_list")
    else:
        form = MasterTemplateForm(instance=template)
    return render(request, "templates_app/template_form.html", {
        "form": form,
        "title": "Template bearbeiten",
    })


@login_required
def template_delete(request, pk):
    template = get_object_or_404(MasterTemplate, pk=pk, created_by=request.user)
    if request.method == "POST":
        template.delete()
        messages.success(request, "Template gelöscht.")
        return redirect("template_list")
    return render(request, "templates_app/template_confirm_delete.html", {
        "template": template,
    })


@login_required
def template_merge(request):
    """View for selecting a template and filling in variables."""
    templates = MasterTemplate.objects.filter(created_by=request.user)
    return render(request, "templates_app/template_merge.html", {
        "templates": templates,
    })


@login_required
def api_template_search(request):
    """Search templates by subject and body (JSON)."""
    q = request.GET.get("q", "").strip()
    templates = MasterTemplate.objects.filter(created_by=request.user)
    if q:
        templates = templates.filter(
            Q(subject__icontains=q) | Q(body__icontains=q)
        )
    results = [
        {"id": t.pk, "name": t.name, "subject": t.subject}
        for t in templates
    ]
    return JsonResponse({"results": results})


@login_required
def api_template_variables(request, pk):
    """Return the variables and template content for a given template (JSON)."""
    template = get_object_or_404(MasterTemplate, pk=pk, created_by=request.user)
    variables = template.extract_variable_names()
    return JsonResponse({
        "id": template.pk,
        "name": template.name,
        "subject": template.subject,
        "body": template.body,
        "variables": variables,
    })


@login_required
def api_template_render(request, pk):
    """Render a template with provided variable values (JSON POST)."""
    if request.method != "POST":
        raise Http404
    template = get_object_or_404(MasterTemplate, pk=pk, created_by=request.user)
    data = json.loads(request.body)
    values = data.get("values", {})
    rendered_subject, rendered_body = template.render(values)
    return JsonResponse({
        "subject": rendered_subject,
        "body": rendered_body,
    })
