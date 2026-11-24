<?php
declare(strict_types=1);

$apiBase = rtrim(getenv('EVA3_API_URL') ?: 'http://127.0.0.1:8000/api', '/');
$apiHost = parse_url($apiBase, PHP_URL_HOST);
$apiScheme = parse_url($apiBase, PHP_URL_SCHEME);
$apiIsLocal = in_array($apiHost, ['127.0.0.1', 'localhost', '::1'], true);
$apiIsValid = in_array($apiScheme, ['http', 'https'], true) && $apiIsLocal;
$adminUsername = getenv('EVA3_ADMIN_USER') ?: '';
$adminPassword = getenv('EVA3_ADMIN_PASSWORD') ?: '';

function escapeHtml($value): string
{
    return htmlspecialchars((string) $value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function fetchApi(string $apiBase, string $resource, string $username = '', string $password = ''): array
{
    $handle = curl_init($apiBase . '/' . rawurlencode($resource) . '/');
    curl_setopt_array($handle, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 3,
        CURLOPT_TIMEOUT => 8,
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_HTTPHEADER => ['Accept: application/json'],
    ]);

    if ($username !== '' && $password !== '') {
        curl_setopt($handle, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
        curl_setopt($handle, CURLOPT_USERPWD, $username . ':' . $password);
    }

    $body = curl_exec($handle);
    $status = (int) curl_getinfo($handle, CURLINFO_HTTP_CODE);
    $curlError = curl_error($handle);
    curl_close($handle);

    if ($body === false) {
        return ['rows' => [], 'error' => 'No fue posible consultar Django: ' . $curlError];
    }

    $payload = json_decode($body, true);
    if ($status < 200 || $status >= 300) {
        $detail = is_array($payload) && isset($payload['detail'])
            ? $payload['detail']
            : 'Django respondió HTTP ' . $status . '.';
        return ['rows' => [], 'error' => (string) $detail];
    }

    if (isset($payload['results']) && is_array($payload['results'])) {
        $rows = $payload['results'];
    } elseif (is_array($payload)) {
        $rows = $payload;
    } else {
        return ['rows' => [], 'error' => 'La API devolvió una respuesta JSON inesperada.'];
    }

    return ['rows' => $rows, 'error' => null];
}

function renderTable(string $title, array $columns, array $result, bool $isSubmissions = false): void
{
    echo '<section class="panel"><div class="panel-heading"><h2>' . escapeHtml($title) . '</h2>';
    if ($result['error'] !== null) {
        echo '<p class="error" role="alert">' . escapeHtml($result['error']) . '</p></div></section>';
        return;
    }

    echo '<span>' . count($result['rows']) . ' registros</span></div>';
    if ($result['rows'] === []) {
        echo '<p class="empty">No hay registros para mostrar.</p></section>';
        return;
    }

    echo '<div class="table-wrap"><table><thead><tr>';
    foreach ($columns as $label => $field) {
        echo '<th scope="col">' . escapeHtml($label) . '</th>';
    }
    echo '</tr></thead><tbody>';

    foreach ($result['rows'] as $row) {
        echo '<tr>';
        foreach ($columns as $label => $field) {
            $value = $row[$field] ?? '—';
            if ($field === 'activo' && array_key_exists($field, $row)) {
                $value = $value ? 'Sí' : 'No';
            }
            echo '<td>';
            if ($isSubmissions && $field === 'codigo_fuente') {
                echo '<details><summary>Ver código</summary><pre>' . escapeHtml($value) . '</pre></details>';
            } else {
                echo escapeHtml($value);
            }
            echo '</td>';
        }
        echo '</tr>';
    }

    echo '</tbody></table></div></section>';
}

$categories = ['rows' => [], 'error' => null];
$challenges = ['rows' => [], 'error' => null];
$solved = ['rows' => [], 'error' => null];
$submissions = ['rows' => [], 'error' => null];
$configurationError = null;

if (!$apiIsValid) {
    $configurationError = 'EVA3_API_URL debe apuntar a localhost para evitar enviar credenciales a otro servidor.';
} elseif (!function_exists('curl_init')) {
    $configurationError = 'PHP necesita tener habilitada la extensión cURL para consultar la API.';
} else {
    $categories = fetchApi($apiBase, 'categorias');
    $challenges = fetchApi($apiBase, 'retos');
    $solved = fetchApi($apiBase, 'retos-resueltos');

    if ($adminUsername !== '' && $adminPassword !== '') {
        $submissions = fetchApi($apiBase, 'envios', $adminUsername, $adminPassword);
    } else {
        $submissions['error'] = 'Configura EVA3_ADMIN_USER y EVA3_ADMIN_PASSWORD para ver los envíos.';
    }
}

$sections = [
    'Categorías' => ['total' => count($categories['rows']), 'error' => $categories['error']],
    'Retos' => ['total' => count($challenges['rows']), 'error' => $challenges['error']],
    'Retos resueltos' => ['total' => count($solved['rows']), 'error' => $solved['error']],
    'Envíos' => ['total' => count($submissions['rows']), 'error' => $submissions['error']],
];
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Datos de Eva 3 | PHP</title>
    <style>
        :root { color-scheme: light; font-family: "Segoe UI", Arial, sans-serif; color: #172033; background: #f6f8fc; }
        * { box-sizing: border-box; }
        body { margin: 0; }
        header, main { width: min(1120px, calc(100% - 36px)); margin: 0 auto; }
        header { padding: 32px 0 24px; }
        h1 { margin: 0; font-size: clamp(1.7rem, 4vw, 2.4rem); }
        h2 { margin: 0; font-size: 1.05rem; }
        .subtitle, .panel-heading span, .empty { color: #718096; }
        .subtitle { margin: 8px 0 0; }
        .notice, .error { padding: 12px 14px; border-radius: 9px; line-height: 1.55; }
        .notice { margin: 0 0 22px; color: #3158a8; background: #edf2ff; }
        .error { margin: 12px 0 0; color: #a53b3b; background: #fff0f0; }
        .summary { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-bottom: 20px; }
        .summary-card, .panel { padding: 18px; border: 1px solid #e7ebf2; border-radius: 12px; background: #fff; box-shadow: 0 6px 18px #232e4f0a; }
        .summary-card span { color: #718096; font-size: .82rem; }
        .summary-card strong { display: block; margin-top: 6px; font-size: 1.6rem; }
        .panel { margin-bottom: 18px; }
        .panel-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
        .table-wrap { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th, td { padding: 11px 12px; border-bottom: 1px solid #e7ebf2; vertical-align: top; font-size: .88rem; }
        th { color: #718096; background: #f6f8fc; font-size: .78rem; }
        tbody tr:last-child td { border-bottom: 0; }
        td { overflow-wrap: anywhere; }
        pre { max-width: 520px; max-height: 300px; overflow: auto; padding: 12px; border-radius: 8px; color: #e5e9ff; background: #172033; }
        .empty { margin: 0; }
        footer { padding: 16px 0 32px; color: #718096; font-size: .8rem; }
        @media (max-width: 700px) { .summary { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    </style>
</head>
<body>
    <header>
        <h1>Datos de Eva 3</h1>
        <p class="subtitle">Panel PHP de solo lectura conectado a la API REST de Django.</p>
    </header>
    <main>
        <?php if ($configurationError !== null): ?>
            <p class="notice" role="alert"><?= escapeHtml($configurationError) ?></p>
        <?php endif; ?>

        <section class="summary" aria-label="Resumen de registros">
            <?php foreach ($sections as $name => $section): ?>
                <article class="summary-card">
                    <span><?= escapeHtml($name) ?></span>
                    <strong><?= escapeHtml($section['total']) ?></strong>
                </article>
            <?php endforeach; ?>
        </section>

        <?php
        renderTable('Categorías', ['ID' => 'id', 'Nombre' => 'nombre', 'Descripción' => 'descripcion'], $categories);
        renderTable(
            'Retos',
            ['ID' => 'id', 'Título' => 'titulo', 'Categoría' => 'categoria_nombre', 'Dificultad' => 'dificultad', 'Puntos' => 'puntos', 'Activo' => 'activo'],
            $challenges
        );
        renderTable(
            'Retos resueltos',
            ['ID' => 'id', 'Participante' => 'usuario', 'Reto' => 'reto_titulo', 'Puntos' => 'puntos_obtenidos', 'Fecha' => 'fecha_resolucion'],
            $solved
        );
        renderTable(
            'Envíos',
            ['ID' => 'id', 'Participante' => 'usuario', 'Reto' => 'reto_titulo', 'Lenguaje' => 'lenguaje', 'Estado' => 'estado', 'Fecha' => 'fecha_envio', 'Código fuente' => 'codigo_fuente'],
            $submissions,
            true
        );
        ?>
        <footer>La conexión se realiza mediante la API de Django; esta página no modifica ni expone directamente el archivo SQLite.</footer>
    </main>
</body>
</html>
