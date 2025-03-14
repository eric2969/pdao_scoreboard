<?php

    $url = "https://be.pdogs.ntu.im/hardcode/team-contest-scoreboard/30/runs";
    $authToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhY2NvdW50X2lkIjo2ODA1LCJleHBpcmUiOiIyMDI1LTAzLTE4VDE2OjU2OjQwLjg1NjAwNiIsImNhY2hlZF91c2VybmFtZSI6ImVyaWMyOTY5In0.xZ7U5EpFJxk_YyrArTVtQCbAqDraEKWO92A51gc4FvE";

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
