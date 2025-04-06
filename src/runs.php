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
    function get_data($key) {
        if($key == "sid") {
            $sid_file = fopen("credit/sid.txt", "r") or die("Unable to open Scoreboard ID file!");
            $data = trim(fgets($sid_file));
        } else if($key == "auth-token") {
            $token_file = fopen("credit/auth-token.txt", "r") or die("Unable to open Auth token file!");
            $data = trim(fgets($token_file));
        } else if($key == "lock-flag") {
            $frozen_file = fopen("credit/lock_flag.txt", "r") or die("Unable to open lock file!");
            $data = trim(fgets($frozen_file));
            $data = ($data == "true") ? true : false;
        } else {
            die("Invalid key: $key");
        }
        return $data;
    }
    function get_runs($flag){
        $data = apcu_fetch("runs");
        if($data === false) {
            $sid = get_data("sid");
            $authToken = get_data("auth-token");
            $url = "https://be.pdogs.ntu.im/hardcode/team-contest-scoreboard/".$sid."/runs";

            // 初始化 cURL
            $ch = curl_init($url);

            // 設定 cURL 選項
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_HTTPHEADER, [
                "auth-token: $authToken",
                "Content-Type: application/json"
            ]);

            // 執行請求並獲取回應
            $response = curl_exec($ch);

            // 檢查錯誤
            if (curl_errno($ch))
                echo "cURL Error: " . curl_error($ch);
            else
                $data = json_decode($response, true);

            // 關閉 cURL
            curl_close($ch);
            apcu_add("runs", $data, 1);
        }
        if(get_data("lock-flag")) {
            $ContestTime = $data["data"]["time"]["contestTime"];
            foreach($data["data"]["runs"] as $key => $value)
                if($ContestTime - $value["submissionTime"] * 60 <= 3600)
                    $data["data"]["runs"][$key]["result"] = "Pending";
        }
        return $data;
    }
    $runs = get_runs($frozen_flag);
    header('Content-Type: application/json');
    header('access-control-allow-origin: *');
    echo json_encode($runs, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    
?>
