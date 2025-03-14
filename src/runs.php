<?php
    $sid_file = fopen("credit/sid.txt", "r") or die("Unable to open Scoreboard ID file!");
    $sid = trim(fgets($sid_file));
    $url = "https://be.pdogs.ntu.im/hardcode/team-contest-scoreboard/".$sid."/runs";
    $token_file = fopen("credit/auth-token.txt", "r") or die("Unable to open Auth token file!");
    $authToken = trim(fgets($token_file));

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
    if (curl_errno($ch)) {
        echo "cURL Error: " . curl_error($ch);
    } else {
        // 解碼 JSON 並輸出
        $data = json_decode($response, true);
        header('Content-Type: application/json');
        echo json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    }

    // 關閉 cURL
    curl_close($ch);
?>
