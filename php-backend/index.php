<?php
// Heaven Essence API — single front controller.
require __DIR__ . '/lib.php';
cors_headers();

$path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';
// Works both at /api/... and at a nested path like /heaven-essence/api/...
$path = '/' . trim(preg_replace('#^.*?/api(?=/|$)#', '', $path), '/');
if ($path === '') $path = '/';
$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
$parts = array_values(array_filter(explode('/', $path), 'strlen'));
$db = db();

// ---------------------------------------------------------------- health
if ($parts === ['health'] && $method === 'GET') {
    $db->query('SELECT 1');
    json(['status' => 'ok', 'database' => 'connected']);
}

// ---------------------------------------------------------------- token
if ($parts === ['token'] && $method === 'POST') {
    $b = body();
    $stmt = $db->prepare('SELECT id, username, password_hash FROM admins WHERE username = ?');
    $stmt->execute([str($b['username'] ?? '', 80)]);
    $admin = $stmt->fetch();
    if (!$admin || !password_verify((string)($b['password'] ?? ''), $admin['password_hash'])) {
        json(['detail' => 'Invalid credentials.'], 400);
    }
    $token = bin2hex(random_bytes(32));
    $upd = $db->prepare('UPDATE admins SET api_token = ? WHERE id = ?');
    $upd->execute([$token, $admin['id']]);
    json(['token' => $token]);
}

// ---------------------------------------------------------------- catalogue (public, read-only)
if (($parts[0] ?? '') === 'catalog' && $method === 'GET') {
    $resource = $parts[1] ?? '';
    $id = $parts[2] ?? null;

    if ($resource === 'categories') {
        $rows = $db->query('SELECT c.id, c.name, c.slug, c.description,
            (SELECT COUNT(*) FROM flavours f WHERE f.category_id = c.id AND f.is_active = 1) AS flavour_count
            FROM categories c ORDER BY c.sort_order, c.name')->fetchAll();
        json(['results' => $rows]);
    }

    if ($resource === 'flavours') {
        if ($id === 'grouped') {
            $out = [];
            foreach ($db->query('SELECT id, name, slug FROM categories ORDER BY sort_order') as $cat) {
                $stmt = $db->prepare('SELECT id, name, swahili_name, slug, description, image, accent_color, notes
                    FROM flavours WHERE category_id = ? AND is_active = 1 ORDER BY sort_order');
                $stmt->execute([$cat['id']]);
                $out[] = ['slug' => $cat['slug'], 'name' => $cat['name'], 'flavours' => $stmt->fetchAll()];
            }
            json($out);
        }
        if ($id !== null) {
            $stmt = $db->prepare('SELECT * FROM flavours WHERE slug = ? AND is_active = 1');
            $stmt->execute([$id]);
            json($stmt->fetch() ?: null, $stmt->fetch() ? 200 : 404);
        }
        $sql = 'SELECT f.id, f.name, f.swahili_name, f.slug, f.description, f.image, f.accent_color,
                f.notes, c.name AS category_name, c.slug AS category
                FROM flavours f LEFT JOIN categories c ON c.id = f.category_id WHERE f.is_active = 1';
        $params = [];
        if (!empty($_GET['category'])) { $sql .= ' AND c.slug = ?'; $params[] = $_GET['category']; }
        if (!empty($_GET['q'])) { $sql .= ' AND f.name LIKE ?'; $params[] = '%' . $_GET['q'] . '%'; }
        $sql .= ' ORDER BY f.sort_order, f.name';
        $stmt = $db->prepare($sql); $stmt->execute($params);
        json(['results' => $stmt->fetchAll()]);
    }

    if ($resource === 'gallery') {
        $sql = 'SELECT id, title, image, category, sort_order FROM gallery WHERE is_active = 1';
        $params = [];
        if (!empty($_GET['category'])) { $sql .= ' AND category = ?'; $params[] = $_GET['category']; }
        $sql .= ' ORDER BY sort_order';
        $stmt = $db->prepare($sql); $stmt->execute($params);
        json(['results' => $stmt->fetchAll()]);
    }

    if ($resource === 'faqs') {
        json(['results' => $db->query('SELECT id, question, answer FROM faqs WHERE is_active = 1 ORDER BY sort_order')->fetchAll()]);
    }

    if ($resource === 'testimonials') {
        json(['results' => $db->query('SELECT id, quote, author, location, flavour_tag, rating FROM testimonials WHERE is_active = 1 ORDER BY sort_order')->fetchAll()]);
    }

    if ($resource === 'settings') {
        if ($id !== null) {
            $stmt = $db->prepare('SELECT setting_key AS `key`, setting_value AS value FROM settings WHERE setting_key = ?');
            $stmt->execute([$id]);
            $row = $stmt->fetch();
            json($row ?: null, $row ? 200 : 404);
        }
        json(['results' => $db->query('SELECT setting_key AS `key`, setting_value AS value FROM settings ORDER BY setting_key')->fetchAll()]);
    }
    json(['detail' => 'Not found.'], 404);
}

// ---------------------------------------------------------------- public writes
if ($parts === ['orders'] && $method === 'POST') {
    $b = body();
    $name = str($b['customer_name'] ?? '', 120);
    $phone = str($b['phone'] ?? '', 30);
    if ($name === '' || !valid_phone($phone)) json(['phone' => ['Enter a valid name and phone number.']], 400);
    $qty = max(1, min(500, (int)($b['quantity'] ?? 1)));
    $flavour = str($b['flavour'] ?? '', 120);
    $stmt = $db->prepare('INSERT INTO orders (customer_name, phone, flavour, product_type, quantity, notes) VALUES (?,?,?,?,?,?)');
    $stmt->execute([$name, $phone, $flavour, str($b['product_type'] ?? 'cup', 20), $qty, str($b['notes'] ?? '', 2000)]);
    $orderId = (int)$db->lastInsertId();
    $items = $b['items'] ?? [];
    $total = 0;
    if (is_array($items)) {
        $ins = $db->prepare('INSERT INTO order_items (order_id, flavour, product_type, quantity) VALUES (?,?,?,?)');
        $names = [];
        foreach ($items as $it) {
            if (!is_array($it)) continue;
            $f = str($it['flavour'] ?? '', 80);
            $q = max(1, min(500, (int)($it['quantity'] ?? 1)));
            $ins->execute([$orderId, $f, str($it['product_type'] ?? 'cup', 20), $q]);
            $total += $q; $names[] = $f;
        }
        if ($names) {
            $db->prepare('UPDATE orders SET flavour = ?, quantity = ? WHERE id = ?')->execute([implode(', ', $names), $total, $orderId]);
        }
    }
    notify("New order #$orderId — $name", "Phone: $phone\nFlavour: $flavour\nQuantity: $qty\nNotes: " . ($b['notes'] ?? ''));
    $row = $db->query("SELECT * FROM orders WHERE id = $orderId")->fetch();
    json($row, 201);
}

if ($parts === ['enquiries'] && $method === 'POST') {
    $b = body();
    $name = str($b['name'] ?? '', 120); $phone = str($b['phone'] ?? '', 30);
    if ($name === '' || !valid_phone($phone)) json(['phone' => ['Enter a valid name and phone number.']], 400);
    $date = ($b['event_date'] ?? '') !== '' ? preg_replace('/[^\d-]/', '', (string)$b['event_date']) : null;
    $stmt = $db->prepare('INSERT INTO enquiries (name, phone, event_type, event_date, guests, flavours, message) VALUES (?,?,?,?,?,?,?)');
    $stmt->execute([$name, $phone, str($b['event_type'] ?? 'other', 20), $date,
        int_or_null($b['guests'] ?? null), str($b['flavours'] ?? '', 255), str($b['message'] ?? '', 4000)]);
    $id = (int)$db->lastInsertId();
    notify("New event enquiry #$id — $name", "Phone: $phone\nEvent: " . ($b['event_type'] ?? '') . "\nDate: $date\nGuests: " . ($b['guests'] ?? '') . "\nMessage: " . ($b['message'] ?? ''));
    json($db->query("SELECT * FROM enquiries WHERE id = $id")->fetch(), 201);
}

if ($parts === ['contact'] && $method === 'POST') {
    $b = body();
    $name = str($b['name'] ?? '', 120); $message = str($b['message'] ?? '', 4000);
    if ($name === '' || mb_strlen($message) < 5) json(['message' => ['Please include your name and a message.']], 400);
    $stmt = $db->prepare('INSERT INTO messages (name, phone, email, subject, message) VALUES (?,?,?,?,?)');
    $stmt->execute([$name, str($b['phone'] ?? '', 30), str($b['email'] ?? '', 120), str($b['subject'] ?? '', 160), $message]);
    $id = (int)$db->lastInsertId();
    notify("New contact message — $name", "From: $name " . ($b['email'] ?? '') . "\nSubject: " . ($b['subject'] ?? '') . "\n\n$message");
    json($db->query("SELECT * FROM messages WHERE id = $id")->fetch(), 201);
}

// ---------------------------------------------------------------- staff endpoints
$resource = $parts[0] ?? '';
if (in_array($resource, ['orders', 'enquiries', 'contact', 'dashboard'], true)) {
    require_staff();

    if ($resource === 'dashboard' && $method === 'GET') {
        $one = fn(string $sql) => (int)$db->query($sql)->fetchColumn();
        json([
            'orders' => $one('SELECT COUNT(*) FROM orders'),
            'new_orders' => $one("SELECT COUNT(*) FROM orders WHERE status='new'"),
            'enquiries' => $one('SELECT COUNT(*) FROM enquiries'),
            'new_enquiries' => $one("SELECT COUNT(*) FROM enquiries WHERE status='new'"),
            'unread_messages' => $one('SELECT COUNT(*) FROM messages WHERE is_read=0'),
            'orders_by_status' => $db->query('SELECT status, COUNT(*) n FROM orders GROUP BY status')->fetchAll(PDO::FETCH_KEY_PAIR),
        ]);
    }

    $table = ['orders' => 'orders', 'enquiries' => 'enquiries', 'contact' => 'messages'][$resource];

    if ($method === 'GET' && count($parts) === 1) {
        json(['results' => $db->query("SELECT * FROM $table ORDER BY id DESC LIMIT 200")->fetchAll()]);
    }

    if ($method === 'PATCH' && count($parts) >= 2) {
        $id = (int)$parts[1];
        $action = $parts[2] ?? '';
        $b = body();
        if ($action === 'status') {
            $allowed = $resource === 'orders'
                ? ['new','confirmed','preparing','ready','completed','cancelled']
                : ['new','contacted','quoted','booked','closed'];
            if (!in_array($b['status'] ?? '', $allowed, true)) json(['detail' => 'Invalid status.'], 400);
            $stmt = $db->prepare("UPDATE $table SET status = ? WHERE id = ?");
            $stmt->execute([$b['status'], $id]);
        } elseif ($action === 'read' && $resource === 'contact') {
            $db->prepare('UPDATE messages SET is_read = 1 WHERE id = ?')->execute([$id]);
        } else {
            json(['detail' => 'Not found.'], 404);
        }
        json($db->query("SELECT * FROM $table WHERE id = $id")->fetch());
    }
}

json(['detail' => 'Not found.'], 404);
