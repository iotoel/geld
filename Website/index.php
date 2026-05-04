<?php
session_start();
if (!($_SESSION['logged_in'] ?? false)) {
    header('Location: login.php');
    exit;
}

$file = __DIR__ . '/data.json';
if (!file_exists($file)) file_put_contents($file, json_encode([]));
$data = json_decode(file_get_contents($file), true);

function nextId($data) {
    if (empty($data)) return 1;
    return max(array_column($data, 'id')) + 1;
}

function isCashWithdrawal($entry) {
    return $entry['desc'] === 'Bezug';
}

// Monat-Formatter (ohne intl)
$monthsDe = [
    '01' => 'Jan', '02' => 'Feb', '03' => 'Mär',
    '04' => 'Apr', '05' => 'Mai', '06' => 'Jun',
    '07' => 'Jul', '08' => 'Aug', '09' => 'Sep',
    '10' => 'Okt', '11' => 'Nov', '12' => 'Dez'
];

function formatMonth($key) {
    global $monthsDe;
    [$y, $m] = explode('-', $key);
    return $monthsDe[$m] . ' ' . $y;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $rawDate  = trim($_POST['date']);
    $rawPrice = floatval($_POST['price']);
    $desc     = trim($_POST['desc']);

    $dateObj = DateTime::createFromFormat(
        '!d.m.Y',
        date('d.m.Y', strtotime(str_replace('/', '.', $rawDate)))
    );
    if (!$dateObj) $dateObj = new DateTime();

    $price = round($rawPrice * 20) / 20;

    $data[] = [
        'id'    => nextId($data),
        'date'  => $dateObj->format('Y-m-d'),
        'price' => $price,
        'desc'  => $desc
    ];

    file_put_contents($file, json_encode($data, JSON_PRETTY_PRINT));
    header("Location: index.php");
    exit;
}

// Monatsauswertung
$months = [];
$cashStats = [];

foreach ($data as $entry) {
    $key = substr($entry['date'], 0, 7);

    if (!isset($months[$key])) {
        $months[$key] = 0;
        $cashStats[$key] = ['count' => 0, 'sum' => 0];
    }

    if (isCashWithdrawal($entry)) {
        $cashStats[$key]['count']++;
        $cashStats[$key]['sum'] += $entry['price'];
    } else {
        $months[$key] += $entry['price'];
    }
}

ksort($months);
ksort($cashStats);
?>
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Einkäufe</title>
<style>
body { font-family: sans-serif; margin: 20px; }
label { display: block; margin-top: 10px; }
input { padding: 5px; }

table { border-collapse: collapse; margin-top: 10px; }
th, td { border: 1px solid #aaa; padding: 6px; }

.neg { color: #cc4444; }

.button {
    background: #0078d4;
    color: white;
    border: none;
    padding: 8px 12px;
    cursor: pointer;
    border-radius: 5px;
    font-size: 13px;
    margin-top: 10px;
    text-decoration: none;
    display: inline-block;
}
.button:hover {
    background: #005a9e;
}
</style>
</head>
<body>

<h2>Neue Ausgabe erfassen</h2>
<form method="POST">
    <label>Datum
        <input type="text" name="date" value="<?php echo date('d.m.Y'); ?>" onfocus="this.select()">
    </label>
    <label>Preis in CHF
        <input type="number" step="0.05" name="price" value="-0" required onfocus="this.select()">
    </label>
    <label>Beschreibung
        <input type="text" name="desc" value="Bezug" required onfocus="this.select()">
    </label>
    <button class="button" type="submit">Speichern</button>
</form>

<h2>Monatsübersicht (ohne Bargeldbezüge)</h2>
<?php foreach ($months as $key => $sum): ?>
    <?php
        $out = number_format($sum, 2);
        if ($sum < 0) $out = '<span class="neg">'.$out.'</span>';
    ?>
    <a class="button" href="month.php?m=<?php echo $key; ?>">
        <?php echo formatMonth($key); ?> (<?php echo $out; ?>)
    </a>
<?php endforeach; ?>

<h2>Bargeldbezüge</h2>
<table>
<tr>
    <th>Monat</th>
    <th>Anzahl Bezüge</th>
    <th>Summe CHF</th>
</tr>
<?php foreach ($cashStats as $month => $stats): ?>
    <?php if ($stats['count'] == 0) continue; ?>
    <tr>
        <td><?php echo formatMonth($month); ?></td>
        <td><?php echo $stats['count']; ?></td>
        <td>
            <?php
                $s = number_format($stats['sum'], 2);
                echo $stats['sum'] < 0 ? "<span class=\"neg\">$s</span>" : $s;
            ?>
        </td>
    </tr>
<?php endforeach; ?>
</table>

</body>
</html>