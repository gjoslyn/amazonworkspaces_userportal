<a href="http://workspaces.lacounty.isd.gov">
   <button>Back</button>
</a>

<?php
//echo exec('whoami');

$username = $_GET["username"];
$pcmurl = $_GET["pcmurl"];
//echo $pcm-url;

$cmd = `export DISPLAY=:0; pcoip-client -fullscreen -b $pcmurl -u $username`;

//exec('bash -c "exec nohup setsid $cmd > /dev/null 2>&1 &"');
exec('nohup ' . $cmd . ' >> /dev/null 2>&1 & echo $!', $pid);

header("Location: ".$_SERVER['HTTP_REFERER'])

?>

