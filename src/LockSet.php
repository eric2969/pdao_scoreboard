<?php
    $debug = false; // Set to true to enable debug mode
    if($debug) {
        error_reporting(E_ALL);
        ini_set('display_errors', 1);
        ini_set('display_startup_errors', 1);
    } else {
        error_reporting(0);
        ini_set('display_errors', 0);
        ini_set('display_startup_errors', 0);
    }
    $token_file = fopen("credit/Unlock-token.txt", "r") or die("Unable to open Auth token file!");
    $token = trim(fgets($token_file));
    fclose($token_file);
    echo $token;
?>