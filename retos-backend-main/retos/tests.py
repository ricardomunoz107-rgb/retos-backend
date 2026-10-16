from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import PermissionDenied

from .models import Categoria, Envio, Reto, RetoResuelto
from .validadores import ejecutar_codigo_restringido
from .admin import RetoResueltoAdmin


class HomeViewTests(TestCase):
    def test_home_displays_challenges_without_project_folders(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Desafíos Disponibles")
        self.assertNotContains(response, "Carpetas del proyecto")

    def test_home_shows_database_challenges_and_statistics(self):
        categoria = Categoria.objects.create(nombre="Algoritmos")
        Reto.objects.create(
            titulo="Suma de arreglos",
            descripcion="Suma los elementos de una lista.",
            dificultad="FACIL",
            puntos=15,
            categoria=categoria,
        )

        response = self.client.get(reverse("home"))

        self.assertContains(response, "Suma de arreglos")
        self.assertContains(response, "15 pts")
        self.assertContains(response, "Fácil")


class ApiTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_authenticate(user=self.admin)

    def test_category_and_challenge_endpoints_support_crud(self):
        category_response = self.client.post(
            "/api/categorias/",
            {"nombre": "Algoritmos", "descripcion": "Retos de algoritmos."},
            format="json",
        )

        self.assertEqual(category_response.status_code, 201)
        category_id = category_response.data["id"]

        challenge_response = self.client.post(
            "/api/retos/",
            {
                "titulo": "Suma de arreglos",
                "descripcion": "Suma los elementos de una lista.",
                "dificultad": "FACIL",
                "puntos": 15,
                "activo": True,
                "categoria": category_id,
            },
            format="json",
        )

        self.assertEqual(challenge_response.status_code, 201)
        self.assertEqual(challenge_response.data["categoria_nombre"], "Algoritmos")
        self.assertNotIn("respuesta_correcta", challenge_response.data)
        self.assertEqual(self.client.get("/api/retos/").status_code, 200)

    def test_submission_endpoint_exposes_challenge_title(self):
        category = Categoria.objects.create(nombre="Algoritmos")
        challenge = Reto.objects.create(
            titulo="Suma de arreglos",
            descripcion="Suma los elementos de una lista.",
            categoria=category,
        )

        response = self.client.post(
            "/api/envios/",
            {
                "reto": challenge.id,
                "usuario": "estudiante",
                "codigo_fuente": "print(sum([1, 2]))",
                "lenguaje": "python",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["reto_titulo"], "Suma de arreglos")

    def test_challenge_api_requires_admin_to_prevent_answer_and_score_tampering(self):
        self.client.force_authenticate(user=None)

        self.assertEqual(self.client.get("/api/retos/").status_code, 200)
        response = self.client.post(
            "/api/retos/",
            {"titulo": "Trampa", "descripcion": "No debería poder crearlo."},
            format="json",
        )

        self.assertEqual(response.status_code, 403)


class PracticePageTests(TestCase):
    def setUp(self):
        self.category = Categoria.objects.create(nombre="Fundamentos")
        self.challenge = Reto.objects.create(
            titulo="Suma de prueba",
            descripcion="¿Cuánto es 2 + 3?",
            puntos=10,
            categoria=self.category,
            respuesta_correcta="5",
        )

    def test_correct_answer_awards_points_once(self):
        url = reverse("resolver_reto", args=[self.challenge.id])
        codigo = "print(2 + 3)"
        response = self.client.post(url, {"usuario": "Ricardo", "codigo_fuente": codigo})

        self.assertRedirects(
            response,
            f"{reverse('detalle_reto', args=[self.challenge.id])}?usuario=Ricardo",
            fetch_redirect_response=False,
        )
        resolucion = RetoResuelto.objects.get(usuario="ricardo", reto=self.challenge)
        self.assertEqual(resolucion.puntos_obtenidos, 10)
        envio = Envio.objects.get(reto=self.challenge)
        self.assertEqual(envio.estado, "ACEPTADO")
        self.assertEqual(envio.usuario, "Ricardo")
        self.assertEqual(envio.codigo_fuente, codigo)

        self.client.post(url, {"usuario": "RICARDO", "codigo_fuente": codigo})

        self.assertEqual(RetoResuelto.objects.filter(usuario="ricardo", reto=self.challenge).count(), 1)
        self.assertEqual(Envio.objects.filter(reto=self.challenge).count(), 2)

    def test_wrong_answer_does_not_award_points(self):
        response = self.client.post(
            reverse("resolver_reto", args=[self.challenge.id]),
            {"usuario": "Ricardo", "codigo_fuente": "print(2 + 2)"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(RetoResuelto.objects.exists())
        self.assertEqual(Envio.objects.get(reto=self.challenge).estado, "RECHAZADO")

    def test_home_and_challenge_selection_link_to_separate_solver_page(self):
        home = self.client.get(reverse("home"))
        self.assertContains(home, reverse("detalle_reto", args=[self.challenge.id]))

        selection = self.client.get(reverse("jugar"))
        self.assertContains(selection, reverse("detalle_reto", args=[self.challenge.id]))
        self.assertContains(selection, "Resolver reto")

        solver = self.client.get(reverse("detalle_reto", args=[self.challenge.id]))
        self.assertContains(solver, "Tu solución en Python")
        self.assertContains(solver, "Ejecutar y comprobar")

    def test_play_page_shows_saved_scoreboard_and_difficulty_groups(self):
        RetoResuelto.objects.create(
            usuario="ricardo",
            reto=self.challenge,
            puntos_obtenidos=self.challenge.puntos,
        )

        response = self.client.get(reverse("jugar"), {"usuario": "Ricardo"})

        self.assertContains(response, "Suma de prueba")
        self.assertContains(response, "10 pts")
        self.assertContains(response, "Reto completado")
        self.assertContains(response, "Fáciles")
        self.assertContains(response, "Medios")
        self.assertContains(response, "Difíciles")
        self.assertContains(response, "Registro de participantes")

    def test_participant_register_includes_unsolved_attempts_and_aggregates_name_case(self):
        other_challenge = Reto.objects.create(
            titulo="Otro reto",
            descripcion="Segundo ejercicio",
            puntos=15,
            categoria=self.category,
            respuesta_correcta="15",
        )
        Envio.objects.create(
            reto=self.challenge,
            usuario="Ana",
            codigo_fuente="print(0)",
            estado="RECHAZADO",
        )
        Envio.objects.create(
            reto=other_challenge,
            usuario="ANA",
            codigo_fuente="print(15)",
            estado="ACEPTADO",
        )
        RetoResuelto.objects.create(
            usuario="ana",
            reto=other_challenge,
            puntos_obtenidos=15,
        )
        Envio.objects.create(
            reto=self.challenge,
            usuario="Bruno",
            codigo_fuente="print(0)",
            estado="RECHAZADO",
        )

        response = self.client.get(reverse("jugar"))
        registros = response.context["registro_participantes"]
        ana = next(participante for participante in registros if participante["usuario"] == "ANA")
        bruno = next(participante for participante in registros if participante["usuario"] == "Bruno")

        self.assertEqual(len(registros), 2)
        self.assertEqual(ana["ejercicios"], 1)
        self.assertEqual(ana["puntos"], 15)
        self.assertIsNotNone(ana["ultima_actividad"])
        self.assertEqual(bruno["ejercicios"], 0)
        self.assertEqual(bruno["puntos"], 0)
        self.assertContains(response, "Registro de participantes")
        self.assertContains(response, "Última actividad (UTC)")

    def test_admin_participant_register_requires_admin_access(self):
        register_url = reverse("admin:registro_participantes")
        self.assertRedirects(
            self.client.get(register_url),
            f"{reverse('admin:login')}?next={register_url}",
        )

    def test_admin_participant_register_displays_aggregated_data(self):
        Envio.objects.create(
            reto=self.challenge,
            usuario="AdminViewUser",
            codigo_fuente="print(2 + 3)",
            estado="ACEPTADO",
        )
        RetoResuelto.objects.create(
            usuario="adminviewuser",
            reto=self.challenge,
            puntos_obtenidos=10,
        )
        admin_user = get_user_model().objects.create_superuser(
            username="site-admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin_user)

        changelist = self.client.get(reverse("admin:retos_retoresuelto_changelist"))
        self.assertContains(changelist, reverse("admin:registro_participantes"))

        response = self.client.get(reverse("admin:registro_participantes"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AdminViewUser")
        self.assertContains(response, "10 pts")
        self.assertContains(response, "Ejercicios resueltos")

    def test_participant_register_admin_permission_is_required(self):
        model_admin = RetoResueltoAdmin(RetoResuelto, AdminSite())
        non_staff_user = get_user_model().objects.create_user(
            username="regular-user",
            password="test-password",
        )
        request = type("Request", (), {"user": non_staff_user})()

        with self.assertRaises(PermissionDenied):
            model_admin.registro_participantes_view(request)

    def test_restricted_validator_supports_basic_python_and_rejects_imports(self):
        url = reverse("resolver_reto", args=[self.challenge.id])
        respuesta = self.client.post(
            url,
            {
                "usuario": "Ricardo",
                "codigo_fuente": "n = 5\nif n == 5:\n    print(len('python') - 1)",
            },
        )

        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(RetoResuelto.objects.filter(reto=self.challenge).exists())

        RetoResuelto.objects.all().delete()
        respuesta = self.client.post(
            url,
            {"usuario": "Ricardo", "codigo_fuente": "import os\nprint(5)"},
        )

        self.assertEqual(respuesta.status_code, 302)
        self.assertFalse(RetoResuelto.objects.exists())
        self.assertEqual(Envio.objects.filter(reto=self.challenge).count(), 2)

    def test_restricted_validator_handles_a_bounded_for_loop(self):
        salida = ejecutar_codigo_restringido(
            "total = 0\nfor numero in range(1, 5):\n    total += numero\nprint(total)"
        )

        self.assertEqual(salida, "10")


class SeededChallengeTests(TestCase):
    def test_play_page_lists_twelve_challenges_across_difficulties(self):
        response = self.client.get(reverse("jugar"))

        self.assertEqual(response.context["total_retos"], 12)
        self.assertEqual(response.context["retos_por_dificultad"][0]["retos"].count(), 4)
        self.assertEqual(response.context["retos_por_dificultad"][1]["retos"].count(), 4)
        self.assertEqual(response.context["retos_por_dificultad"][2]["retos"].count(), 4)

    def test_all_twelve_challenges_have_a_valid_python_solution(self):
        solutions = {
            "Suma de dos números": "print(7 + 5)",
            "Condicional par o impar": (
                "numero = 8\n"
                "if numero % 2 == 0:\n"
                "    print(True)\n"
                "else:\n"
                "    print(False)"
            ),
            "Contar caracteres": 'palabra = "python"\nprint(len(palabra))',
            "Área de un rectángulo": "base = 4\naltura = 3\nprint(base * altura)",
            "Suma acumulada": (
                "total = 0\n"
                "for numero in range(1, 6):\n"
                "    total += numero\n"
                "print(total)"
            ),
            "Factorial de cinco": (
                "resultado = 1\n"
                "for numero in range(1, 6):\n"
                "    resultado *= numero\n"
                "print(resultado)"
            ),
            "FizzBuzz del uno al cinco": (
                "for numero in range(1, 6):\n"
                "    if numero % 3 == 0:\n"
                '        print("Fizz")\n'
                "    elif numero % 5 == 0:\n"
                '        print("Buzz")\n'
                "    else:\n"
                "        print(numero)"
            ),
            "Mayor de una lista": "print(max([4, 9, 2, 7]))",
            "Suma de números pares": (
                "total = 0\n"
                "for numero in range(1, 11):\n"
                "    if numero % 2 == 0:\n"
                "        total += numero\n"
                "print(total)"
            ),
            "Comprobar si un número es primo": (
                "numero = 7\n"
                "es_primo = True\n"
                "for divisor in range(2, numero):\n"
                "    if numero % divisor == 0:\n"
                "        es_primo = False\n"
                "print(es_primo)"
            ),
            "Secuencia de Fibonacci": (
                "anterior = 0\n"
                "actual = 1\n"
                "for paso in range(6):\n"
                "    siguiente = anterior + actual\n"
                "    anterior = actual\n"
                "    actual = siguiente\n"
                "print(anterior)"
            ),
            "Tabla del siete": (
                "for numero in range(1, 11):\n"
                "    print(7 * numero)"
            ),
        }

        self.assertEqual(Reto.objects.count(), 12)
        for reto in Reto.objects.all():
            with self.subTest(reto=reto.titulo):
                salida = ejecutar_codigo_restringido(solutions[reto.titulo])
                self.assertEqual(
                    " ".join(salida.casefold().split()),
                    " ".join(reto.respuesta_correcta.casefold().split()),
                )

    def test_seeded_challenges_are_accepted_and_persist_attempts_and_points(self):
        reto = Reto.objects.get(titulo="Tabla del siete")

        response = self.client.post(
            reverse("resolver_reto", args=[reto.id]),
            {
                "usuario": "alumna",
                "codigo_fuente": (
                    "for numero in range(1, 11):\n"
                    "    print(7 * numero)"
                ),
            },
        )

        self.assertEqual(response.status_code, 302)
        envio = Envio.objects.get(reto=reto, usuario="alumna")
        self.assertEqual(envio.estado, "ACEPTADO")
        self.assertIn("print(7 * numero)", envio.codigo_fuente)
        resolucion = RetoResuelto.objects.get(reto=reto, usuario="alumna")
        self.assertEqual(resolucion.puntos_obtenidos, reto.puntos)
