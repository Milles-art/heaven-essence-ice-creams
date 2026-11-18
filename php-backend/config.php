<?php
// cPanel deployment configuration. Keep this file private (not public_html).
return [
    'db_host' => 'localhost',
    'db_name' => 'CHANGE_ME_DB_NAME',
    'db_user' => 'CHANGE_ME_DB_USER',
    'db_pass' => 'CHANGE_ME_DB_PASSWORD',
    'db_charset' => 'utf8mb4',

    // Frontend origins allowed to call this API (comma separated).
    'cors_origins' => [
        'https://familychoiceminimarket.co.tz',
        'https://www.familychoiceminimarket.co.tz',
        'http://localhost:4173',
    ],

    // Notifications
    'email_to' => 'info@familychoiceminimarket.co.tz',

    // Admin created by setup.php (password shown once).
    'admin_user' => 'admin',
];
