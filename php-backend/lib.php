<?php
// Shared helpers for the PHP API and admin panel.

function config(): array {
    static $cfg = null;
    if ($cfg === null) $cfg = require __DIR__ . '/config.php';
    return $cfg;
}

function db(): PDO {
    static $pdo = null;
    if ($pdo !== null) return $pdo;
    $c = config();
    $dsn = "mysql:host={$c['db_host']};dbname={$c['db_name']};charset={$c['db_charset']}";
    $pdo = new PDO($dsn, $c['db_user'], $c['db_pass'], [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
    ]);
    return $pdo;
}

function cors_headers(): void {
    $origin = $_SERVER['HTTP_ORIGIN'] ?? '';
    if ($origin !== '' && in_array($origin, config()['cors_origins'], true)) {
        header('Access-Control-Allow-Origin: ' . $origin);
        header('Vary: Origin');
        header('Access-Control-Allow-Credentials: true');
    }
    header('Access-Control-Allow-Methods: GET, POST, PATCH, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, Authorization');
    if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') {
        http_response_code(204);
        exit;
    }
}

function json(mixed $data, int $status = 200): never {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function body(): array {
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true);
    return is_array($data) ? $data : [];
}

function str(mixed $v, int $max = 255): string {
    return mb_substr(trim((string)($v ?? '')), 0, $max);
}

function int_or_null(mixed $v): ?int {
    if ($v === null || $v === '') return null;
    return is_numeric($v) ? (int)$v : null;
}

function valid_phone(string $phone): bool {
    return strlen(preg_replace('/[^0-9+]/', '', $phone)) >= 9;
}

function notify(string $subject, string $message): void {
    $to = config()['email_to'];
    @mail($to, $subject, $message, 'From: ' . $to . "\r\nContent-Type: text/plain; charset=UTF-8");
}

function settings(): array {
    $out = [];
    foreach (db()->query('SELECT setting_key, setting_value FROM settings') as $row) {
        $out[$row['setting_key']] = $row['setting_value'];
    }
    return $out;
}

function staff_authenticated(): bool {
    if (session_status() === PHP_SESSION_NONE) session_start();
    return !empty($_SESSION['admin_id']);
}

function token_user(): ?array {
    $auth = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    if (!preg_match('/^Token\s+(.+)$/i', $auth, $m)) return null;
    $stmt = db()->prepare('SELECT id, username FROM admins WHERE api_token = ?');
    $stmt->execute([$m[1]]);
    $row = $stmt->fetch();
    return $row ?: null;
}

function require_staff(): void {
    if (staff_authenticated() || token_user()) return;
    json(['detail' => 'Authentication required.'], 403);
}

function slugify(string $s): string {
    $s = strtolower($s);
    $s = str_replace(['&', ' '], ['and', '-'], $s);
    return preg_replace('/[^a-z0-9-]/', '', $s);
}
