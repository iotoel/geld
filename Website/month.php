<?php
session_start();
if (!($_SESSION['logged_in'] ?? false)) {
    header('Location: login.php');
    exit;
}

$file = __DIR__ . '/data.json';
$data = json_decode(file_get_contents($file), true);

$month = $_GET['m'] ?? '';
$entries = array_filter($data, fn($e) => strpos($e['date'], $month) === 0);
usort($entries, fn($a,$b) => strcmp($a['date'],$b['date']));

// Monat-Formatter (ohne intl)
$monthsDe = [
    '01' => 'Januar', '02' => 'Februar', '03' => 'März',
    '04' => 'April', '05' => 'Mai', '06' => 'Juni',
    '07' => 'Juli', '08' => 'August', '09' => 'September',
    '10' => 'Oktober', '11' => 'November', '12' => 'Dezember'
];

function formatMonthFull($key) {
    global $monthsDe;
    [$y, $m] = explode('-', $key);
    return $monthsDe[$m] . ' ' . $y;
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Monatsansicht: <?php echo htmlspecialchars($month); ?></title>
<style>
table { border-collapse: collapse; }
th, td { border: 1px solid #aaa; padding: 6px; }
.neg { color: #c00; }

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

<h2><?php echo formatMonthFull($month); ?></h2>

<table>
<tr>
    <th>Datum</th>
    <th>Preis</th>
    <th>Beschreibung</th>
    <th>Aktion</th>
</tr>
<?php foreach ($entries as $e): ?>
<tr>
    <td><?php echo date('d.m.Y', strtotime($e['date'])); ?></td>
    <td>
        <?php
            $p = number_format($e['price'], 2);
            echo $e['price'] < 0 ? "<span class=\"neg\">$p</span>" : $p;
        ?>
    </td>
    <td><?php echo htmlspecialchars($e['desc']); ?></td>
    <td>
        <a class="button" href="edit.php?id=<?php echo $e['id']; ?>">Ändern</a>
        <a class="button" href="delete.php?id=<?php echo $e['id']; ?>">Löschen</a>
    </td>
</tr>
<?php endforeach; ?>
</table>

<br>
<a class="button" href="index.php">Zurück</a>

</body>
</html>