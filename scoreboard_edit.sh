read -p "Board ID: " board_id
read -p "Auth Token: " auth_token
read -a problem_id -p "Problem ID: "
read -p "Penalty: " penalty
list=$(printf "%s, " ${problem_id[@]})
list='['${list::-2}']'
curl -X 'PATCH' "https://be.pdogs.ntu.im/team-contest-scoreboard/""$id" \
    -H "auth-token: ""$auth_token" \
    -H "Content-Type: application/json" \
    -d '{
          "challenge_label": "aaa",
          "title": "aaa",
          "target_problem_ids":'"$list"',
          "penalty_formula": "solved_time_mins * 1 + wrong_submissions * '"$penalty"',
          "team_label_filter": ""
        }'