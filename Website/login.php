<?php
session_start();

// Passwort aus .env laden
$env = parse_ini_file(__DIR__ . '/.env');
$PASSWORD = $env['PASSWORD'] ?? 'defaultPasswort';

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $pass = $_POST['password'] ?? '';
    if ($pass === $PASSWORD) {
        $_SESSION['logged_in'] = true;
        header('Location: index.php');
        exit;
    } else {
        $error = 'Falsches Passwort!';
    }
}
?>

<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Login</title>
<style>
body { font-family:sans-serif; padding:20px; }
input { padding:5px; margin-top:5px; }
.button { padding:8px 12px; background:#0078d4; color:white; border:none; border-radius:5px; cursor:pointer; }
.button:hover { background:#005a9e; }
.error { color:red; }
</style>
</head>
<body>
<h2>Login</h2>
<form method="POST">
    <label>Passwort:
        <input type="password" name="password" required>
    </label>
    <br>
    <button type="submit" class="button">Login</button>
</form>
<?php if($error) echo "<p class='error'>$error</p>"; ?>
</body>
</html>
