curl -X 'PATCH' "https://be.pdogs.ntu.im/team-contest-scoreboard/30" \
    -H "auth-token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhY2NvdW50X2lkIjo2ODA1LCJleHBpcmUiOiIyMDI1LTAzLTA5VDIyOjU2OjI1LjQ2NzUxMSIsImNhY2hlZF91c2VybmFtZSI6ImVyaWMyOTY5In0.fTmglPhvNGbDneZ-8HfzfoaC_sHZpQUESU7LpqiV9Oc" \
    -H "Content-Type: application/json" \
    -d '{
          "challenge_label": "aaa",
          "title": "aaa",
          "target_problem_ids": [1788, 1797, 1799],
          "penalty_formula": "solved_time_mins * 1 + wrong_submissions * 20",
          "team_label_filter": ""
        }'