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
    $flag = $_GET['flag'];
    if($token != hash('sha256', $_GET['token']))
        die('<b style="color:red; font-weight:bold;">Invalid authorization token</b>');
    if($flag != "true" && $flag != "false")
        die('<b style="font-weight:bold;">Invalid Input Format</b>');
    $flag_file = fopen("credit/lock_flag.txt", "w") or die("Unable to open lock flag file!");
    fwrite($flag_file, $flag);
    fclose($flag_file);
    echo '<b style="font-weight:normal;">Update Scoreboard Lock Flag to <span style="font-weight:bold;">'.$flag.'</span>!</b>';
?>