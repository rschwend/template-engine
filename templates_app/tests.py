import json

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import MasterTemplate, TemplateVariable, Variable


class MasterTemplateModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="testpass123")
        self.template = MasterTemplate.objects.create(
            name="Welcome Mail",
            subject="Hallo {{name}}",
            body="Lieber {{name}}, willkommen bei {{firma}}!",
            created_by=self.user,
        )

    def test_extract_variable_names(self):
        names = self.template.extract_variable_names()
        self.assertEqual(names, ["firma", "name"])

    def test_sync_variables(self):
        self.template.sync_variables()
        self.assertEqual(Variable.objects.count(), 2)
        self.assertEqual(TemplateVariable.objects.count(), 2)

    def test_sync_variables_removes_stale(self):
        self.template.sync_variables()
        self.template.body = "Hallo {{name}}!"
        self.template.save()
        self.template.sync_variables()
        linked = self.template.templatevariable_set.count()
        self.assertEqual(linked, 1)

    def test_render(self):
        subject, body = self.template.render({"name": "Max", "firma": "ACME"})
        self.assertEqual(subject, "Hallo Max")
        self.assertEqual(body, "Lieber Max, willkommen bei ACME!")

    def test_render_partial(self):
        subject, body = self.template.render({"name": "Max"})
        self.assertIn("{{firma}}", body)


class AuthViewsTest(TestCase):
    def test_landing_page(self):
        resp = self.client.get(reverse("landing"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Template Engine")

    def test_signup(self):
        resp = self.client.post(reverse("signup"), {
            "username": "newuser",
            "email": "new@test.de",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    @override_settings(SIGNUP_ENABLED=False)
    def test_signup_disabled(self):
        resp = self.client.get(reverse("signup"))
        self.assertEqual(resp.status_code, 302)

    def test_login(self):
        User.objects.create_user("testuser", password="testpass123")
        resp = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "testpass123",
        })
        self.assertEqual(resp.status_code, 302)


class TemplateCRUDTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="testpass123")
        self.client.login(username="testuser", password="testpass123")

    def test_create_template(self):
        resp = self.client.post(reverse("template_create"), {
            "name": "Test",
            "subject": "Betreff {{var}}",
            "body": "Body {{var}}",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(MasterTemplate.objects.count(), 1)
        t = MasterTemplate.objects.first()
        self.assertEqual(t.templatevariable_set.count(), 1)

    def test_edit_template(self):
        t = MasterTemplate.objects.create(
            name="Old", subject="S", body="B", created_by=self.user
        )
        resp = self.client.post(reverse("template_edit", args=[t.pk]), {
            "name": "New",
            "subject": "S2",
            "body": "B2",
        })
        self.assertEqual(resp.status_code, 302)
        t.refresh_from_db()
        self.assertEqual(t.name, "New")

    def test_delete_template(self):
        t = MasterTemplate.objects.create(
            name="Del", subject="S", body="B", created_by=self.user
        )
        resp = self.client.post(reverse("template_delete", args=[t.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(MasterTemplate.objects.count(), 0)

    def test_list_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse("template_list"))
        self.assertEqual(resp.status_code, 302)

    def test_cannot_edit_others_template(self):
        other = User.objects.create_user("other", password="pass123")
        t = MasterTemplate.objects.create(
            name="Other", subject="S", body="B", created_by=other
        )
        resp = self.client.get(reverse("template_edit", args=[t.pk]))
        self.assertEqual(resp.status_code, 404)


class MergeAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="testpass123")
        self.client.login(username="testuser", password="testpass123")
        self.template = MasterTemplate.objects.create(
            name="Mail",
            subject="Hi {{name}}",
            body="Hallo {{name}}, dein Code: {{code}}",
            created_by=self.user,
        )
        self.template.sync_variables()

    def test_api_variables(self):
        resp = self.client.get(
            reverse("api_template_variables", args=[self.template.pk])
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("name", data["variables"])
        self.assertIn("code", data["variables"])

    def test_api_render(self):
        resp = self.client.post(
            reverse("api_template_render", args=[self.template.pk]),
            data=json.dumps({"values": {"name": "Max", "code": "ABC"}}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["subject"], "Hi Max")
        self.assertEqual(data["body"], "Hallo Max, dein Code: ABC")
