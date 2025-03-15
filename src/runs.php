<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);
    function get_data($key) {
        $data = apcu_fetch($key);
        if ($data === false) {
            // 如果Cache中沒有資料，則從資料庫中獲取
            // 將獲取到的資料存放在Cache中，設置過期時間為10分鐘
            if($key == "sid") {
                $sid_file = fopen("credit/sid.txt", "r") or die("Unable to open Scoreboard ID file!");
                $data = trim(fgets($sid_file));
            } else if($key == "auth-token") {
                $token_file = fopen("credit/auth-token.txt", "r") or die("Unable to open Auth token file!");
                $data = trim(fgets($token_file));
            }
            apcu_add($key, $data, 600);
        }
        return $data;
    }

    function get_runs(){
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
            apcu_add("runs", $data, 2);
        }
        return $data;
    }
    $runs = get_runs();
    header('Content-Type: application/json');
    echo json_encode($runs, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    
?>
