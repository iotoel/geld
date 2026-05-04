<?php
session_start();
if (!($_SESSION['logged_in'] ?? false)) {
    header('Location: login.php');
    exit;
}

$file = __DIR__ . '/data.json';
$data = json_decode(file_get_contents($file), true);

$id = intval($_GET['id'] ?? 0);
$entry = null;

foreach ($data as $e) {
    if ($e['id'] == $id) { $entry = $e; break; }
}

if (!$entry) die("Eintrag nicht gefunden.");

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    foreach ($data as &$e) {
        if ($e['id'] == $id) {
            $rawDate  = trim($_POST['date']);
            $rawPrice = floatval($_POST['price']);
            $desc     = trim($_POST['desc']);

            $dateObj = DateTime::createFromFormat(
                '!d.m.Y',
                date('d.m.Y', strtotime(str_replace('/', '.', $rawDate)))
            );
            if (!$dateObj) $dateObj = new DateTime();

            $e['date']  = $dateObj->format('Y-m-d');
            $e['price'] = round($rawPrice * 20) / 20;
            $e['desc']  = $desc;
        }
    }
    unset($e);

    file_put_contents($file, json_encode($data, JSON_PRETTY_PRINT));
    header("Location: index.php");
    exit;
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Eintrag bearbeiten</title>
<style>
label { display:block; margin-top:10px; }
input { padding:5px; }

.button {
    background: #0078d4;
    color: white;
    border: none;
    padding: 8px 12px;
    cursor: pointer;
    border-radius: 5px;
    font-size: 13px;
    text-decoration: none;
    display: inline-block;
}
.button:hover {
    background: #005a9e;
}
</style>
</head>
<body>

<h2>Ausgabe ändern</h2>

<form method="POST">
    <label>Datum
        <input type="text" name="date" value="<?php echo date('d.m.Y', strtotime($entry['date'])); ?>">
    </label>
    <label>Preis in CHF
        <input type="number" step="0.05" name="price" value="<?php echo $entry['price']; ?>">
    </label>
    <label>Beschreibung
        <input type="text" name="desc" value="<?php echo htmlspecialchars($entry['desc']); ?>">
    </label>
    <button class="button" type="submit">Speichern</button>
</form>

<br>
<a class="button" href="index.php">Abbrechen</a>

</body>
</html>
