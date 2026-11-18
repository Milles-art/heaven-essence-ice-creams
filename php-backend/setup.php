<?php
// One-time CLI setup: php setup.php 'your-admin-password'
require __DIR__ . '/lib.php';

if (PHP_SAPI !== 'cli') { http_response_code(403); exit('CLI only'); }
$password = $argv[1] ?? getenv('ADMIN_PASSWORD');
if (!$password || strlen($password) < 8) {
    fwrite(STDERR, "Usage: php setup.php 'a-strong-admin-password'\n");
    exit(1);
}

$c = config();
$db = db();
$sql = file_get_contents(__DIR__ . '/database.sql');
foreach (array_filter(array_map('trim', explode(';', $sql))) as $statement) {
    if ($statement === '') continue;
    $db->exec($statement . ';');
}

$hash = password_hash($password, PASSWORD_DEFAULT);
$token = bin2hex(random_bytes(32));
$stmt = $db->prepare('SELECT id FROM admins WHERE username = ?');
$stmt->execute([$c['admin_user']]);
if ($stmt->fetch()) {
    $db->prepare('UPDATE admins SET password_hash = ?, api_token = ? WHERE username = ?')
       ->execute([$hash, $token, $c['admin_user']]);
    echo "Admin password + token updated.\n";
} else {
    $db->prepare('INSERT INTO admins (username, password_hash, api_token) VALUES (?,?,?)')
       ->execute([$c['admin_user'], $hash, $token]);
    echo "Admin created.\n";
}

echo "Database: {$c['db_name']}\n";
echo "Admin user: {$c['admin_user']}\n";
echo "API token: $token\n";
echo "Done. Open /admin/ to sign in.\n";
