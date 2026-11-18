<?php
require __DIR__ . '/../lib.php';
if (session_status() === PHP_SESSION_NONE) session_start();
$db = db();

// Login
if (isset($_POST['login'])) {
    $stmt = $db->prepare('SELECT id, username, password_hash FROM admins WHERE username = ?');
    $stmt->execute([str($_POST['username'] ?? '', 80)]);
    $admin = $stmt->fetch();
    if ($admin && password_verify((string)($_POST['password'] ?? ''), $admin['password_hash'])) {
        $_SESSION['admin_id'] = $admin['id'];
        $_SESSION['admin_name'] = $admin['username'];
        header('Location: index.php'); exit;
    }
    $error = 'Invalid username or password.';
}
if (isset($_GET['logout'])) { session_destroy(); header('Location: index.php'); exit; }

// Actions
if (staff_authenticated()) {
    if (isset($_POST['status_table'], $_POST['status_id'], $_POST['status_value'])) {
        $allowed = ['orders', 'enquiries'];
        $table = in_array($_POST['status_table'], $allowed, true) ? $_POST['status_table'] : 'orders';
        $stmt = $db->prepare("UPDATE $table SET status = ? WHERE id = ?");
        $stmt->execute([str($_POST['status_value'], 30), (int)$_POST['status_id']]);
        header('Location: index.php?view=' . urlencode($table)); exit;
    }
    if (isset($_POST['read_id'])) {
        $db->prepare('UPDATE messages SET is_read = 1 WHERE id = ?')->execute([(int)$_POST['read_id']]);
        header('Location: index.php?view=messages'); exit;
    }
    if (isset($_POST['save_key'], $_POST['save_value'])) {
        $db->prepare('INSERT INTO settings (setting_key, setting_value) VALUES (?,?) ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)')
           ->execute([str($_POST['save_key'], 60), str($_POST['save_value'], 2000)]);
        header('Location: index.php?view=settings'); exit;
    }
    if (isset($_GET['export'])) {
        $map = ['orders' => 'orders', 'enquiries' => 'enquiries', 'messages' => 'messages'];
        $table = $map[$_GET['export']] ?? 'orders';
        header('Content-Type: text/csv');
        header('Content-Disposition: attachment; filename="' . $table . '.csv"');
        $out = fopen('php://output', 'w');
        $cols = $db->query("SHOW COLUMNS FROM $table")->fetchAll(PDO::FETCH_COLUMN);
        fputcsv($out, $cols);
        foreach ($db->query("SELECT * FROM $table ORDER BY id DESC") as $row) fputcsv($out, array_values($row));
        fclose($out); exit;
    }
}

$view = $_GET['view'] ?? 'dashboard';
$views = ['dashboard','orders','enquiries','messages','settings'];
if (!in_array($view, $views, true)) $view = 'dashboard';
?>
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Heaven Essence — Admin</title>
<style>
body{font:15px/1.5 system-ui,sans-serif;margin:0;background:#faf6f0;color:#3a2620}
header{background:#402923;color:#fff;padding:14px 22px;display:flex;justify-content:space-between;align-items:center}
header a{color:#fff;text-decoration:none;margin-left:18px;font-size:14px}
main{max-width:1100px;margin:26px auto;padding:0 18px}
nav a{display:inline-block;padding:8px 14px;margin:0 4px 12px 0;border-radius:99px;background:#fff;text-decoration:none;color:#7a3b48;border:1px solid #e9dcd6}
nav a.on{background:#a8324c;color:#fff;border-color:#a8324c}
.card{background:#fff;border:1px solid #e9dcd6;border-radius:16px;padding:18px;margin-bottom:16px}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:8px;border-bottom:1px solid #eee;vertical-align:top}
th{color:#8a5a3c;font-size:11px;text-transform:uppercase;letter-spacing:.08em}
button,input,select{font:inherit;padding:6px 10px;border-radius:8px;border:1px solid #ddd}
button{background:#a8324c;color:#fff;border:0;cursor:pointer}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.stat{background:#fff;border:1px solid #e9dcd6;border-radius:14px;padding:16px;text-align:center}
.stat b{display:block;font-size:28px;color:#a8324c}
.small{font-size:12px;color:#777}
</style></head><body>
<?php if (!staff_authenticated()): ?>
<header><b>Heaven Essence — Admin</b></header><main><div class="card" style="max-width:380px;margin:60px auto">
<h2>Sign in</h2><?php if (!empty($error)) echo '<p style="color:#a8324c">' . htmlspecialchars($error) . '</p>'; ?>
<form method="post"><p><input name="username" placeholder="Username" required style="width:100%"></p>
<p><input name="password" type="password" placeholder="Password" required style="width:100%"></p>
<p><button name="login" value="1">Sign in</button></p></form></div></main>
<?php else: ?>
<header><b>Heaven Essence — Admin</b><span><?= htmlspecialchars($_SESSION['admin_name']) ?> · <a href="?logout=1">Sign out</a></span></header>
<main><nav>
<?php foreach ($views as $v): ?><a class="<?= $v === $view ? 'on' : '' ?>" href="?view=<?= $v ?>"><?= ucfirst($v) ?></a><?php endforeach; ?>
</nav>

<?php if ($view === 'dashboard'):
 $count = fn($s) => (int)$db->query($s)->fetchColumn(); ?>
<div class="stats">
 <div class="stat"><b><?= $count('SELECT COUNT(*) FROM orders') ?></b>Orders</div>
 <div class="stat"><b><?= $count("SELECT COUNT(*) FROM orders WHERE status='new'") ?></b>New orders</div>
 <div class="stat"><b><?= $count('SELECT COUNT(*) FROM enquiries') ?></b>Enquiries</div>
 <div class="stat"><b><?= $count('SELECT COUNT(*) FROM messages WHERE is_read=0') ?></b>Unread messages</div>
</div>
<div class="card"><h3>API token</h3><p class="small">Use <code>POST /api/token/</code> with your admin username and password to get a token for external API calls.</p></div>
<?php endif; ?>

<?php if ($view === 'orders'): ?>
<div class="card"><h3>Orders <a class="small" href="?export=orders">Export CSV</a></h3>
<table><tr><th>ID</th><th>Name</th><th>Phone</th><th>Flavour</th><th>Qty</th><th>Status</th><th></th></tr>
<?php foreach ($db->query('SELECT * FROM orders ORDER BY id DESC LIMIT 200') as $r): ?>
<tr><td>#<?= $r['id'] ?></td><td><?= htmlspecialchars($r['customer_name']) ?></td><td><?= htmlspecialchars($r['phone']) ?></td>
<td><?= htmlspecialchars($r['flavour']) ?></td><td><?= $r['quantity'] ?></td>
<td><form method="post" style="display:flex;gap:4px"><input type="hidden" name="status_table" value="orders"><input type="hidden" name="status_id" value="<?= $r['id'] ?>">
<select name="status_value"><?php foreach (['new','confirmed','preparing','ready','completed','cancelled'] as $s) echo "<option" . ($s === $r['status'] ? ' selected' : '') . ">$s</option>"; ?></select><button>Save</button></form></td>
<td class="small"><?= htmlspecialchars($r['created_at']) ?></td></tr><?php endforeach; ?></table></div>
<?php endif; ?>

<?php if ($view === 'enquiries'): ?>
<div class="card"><h3>Event enquiries <a class="small" href="?export=enquiries">Export CSV</a></h3>
<table><tr><th>ID</th><th>Name</th><th>Phone</th><th>Event</th><th>Date</th><th>Guests</th><th>Status</th></tr>
<?php foreach ($db->query('SELECT * FROM enquiries ORDER BY id DESC LIMIT 200') as $r): ?>
<tr><td>#<?= $r['id'] ?></td><td><?= htmlspecialchars($r['name']) ?></td><td><?= htmlspecialchars($r['phone']) ?></td>
<td><?= htmlspecialchars($r['event_type']) ?></td><td><?= htmlspecialchars($r['event_date'] ?? '') ?></td><td><?= htmlspecialchars($r['guests'] ?? '') ?></td>
<td><form method="post" style="display:flex;gap:4px"><input type="hidden" name="status_table" value="enquiries"><input type="hidden" name="status_id" value="<?= $r['id'] ?>">
<select name="status_value"><?php foreach (['new','contacted','quoted','booked','closed'] as $s) echo "<option" . ($s === $r['status'] ? ' selected' : '') . ">$s</option>"; ?></select><button>Save</button></form></td></tr><?php endforeach; ?></table></div>
<?php endif; ?>

<?php if ($view === 'messages'): ?>
<div class="card"><h3>Contact messages <a class="small" href="?export=messages">Export CSV</a></h3>
<table><tr><th>ID</th><th>Name</th><th>Subject</th><th>Message</th><th>Read</th></tr>
<?php foreach ($db->query('SELECT * FROM messages ORDER BY id DESC LIMIT 200') as $r): ?>
<tr><td>#<?= $r['id'] ?></td><td><?= htmlspecialchars($r['name']) ?></td><td><?= htmlspecialchars($r['subject']) ?></td>
<td><?= nl2br(htmlspecialchars(mb_substr($r['message'], 0, 160))) ?></td>
<td><?php if (!$r['is_read']): ?><form method="post"><input type="hidden" name="read_id" value="<?= $r['id'] ?>"><button>Mark read</button></form><?php else: ?>✓<?php endif; ?></td></tr><?php endforeach; ?></table></div>
<?php endif; ?>

<?php if ($view === 'settings'): ?>
<div class="card"><h3>Site settings</h3>
<table><tr><th>Key</th><th>Value</th></tr>
<?php foreach (settings() as $k => $v): ?>
<tr><td><b><?= htmlspecialchars($k) ?></b></td><td><form method="post" style="display:flex;gap:6px"><input type="hidden" name="save_key" value="<?= htmlspecialchars($k) ?>"><input name="save_value" value="<?= htmlspecialchars($v) ?>" style="width:340px"><button>Save</button></form></td></tr><?php endforeach; ?></table></div>
<?php endif; ?>
</main>
<?php endif; ?>
</body></html>
