<a href="..">
   <button>Back</button>
</a>

<?php

$username = $_GET["username"];
$pcmurl = $_GET["pcmurl"];

$cmd = 'export DISPLAY=:0; pcoip-client -fullscreen=true -b '.escapeshellarg($pcmurl);
$cmd .= ' -u '.escapeshellarg($username);

//exec('nohup ' . $cmd . ' >> /dev/null 2>&1 & echo $!', $pid);

exec("$cmd 2>&1 &", $output, $return_var);
header("Location: ".$_SERVER['HTTP_REFERER']);

?>

