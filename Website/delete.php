<?php
session_start();
if (!($_SESSION['logged_in'] ?? false)) {
    header('Location: login.php');
    exit;
}

$file = __DIR__ . '/data.json';
$data = json_decode(file_get_contents($file), true);

$id = intval($_GET['id'] ?? 0);

$data = array_filter($data, fn($e) => $e['id'] != $id);

file_put_contents($file, json_encode(array_values($data), JSON_PRETTY_PRINT));

header("Location: index.php");
exit;
