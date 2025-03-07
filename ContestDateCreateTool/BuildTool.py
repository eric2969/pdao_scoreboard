import csv, json, requests

def edit_scoreboard(problems):
    print("Updating scoreboard ...")
    sid = input("Enter the scoreboard id: ")
    token = input("Enter the pdogs auth token: ")
    url = f"https://be.pdogs.ntu.im/team-contest-scoreboard/{sid}"
    headers = {
        "auth-token": token,
        "Content-Type": "application/json"
    }
    data = {
        "challenge_label": "X",
        "title": "X",
        "target_problem_ids": problems,
        "penalty_formula": "solved_time_mins * 1 + wrong_submissions * 20",
        "team_label_filter": ""
    }
    response = requests.patch(url, json=data, headers=headers)
    if response.status_code == 200:
        if response.json()["success"]:
            print("Scoreboard has been updated successfully.")
        else:
            print(response.json()['error'])
    else:
        print(f"Error occurred: {response.status_code}")


def csv_to_json(title, problems_csv, teams_csv, json_file_path):
    problems = []
    teams = []
    pid = []
    with open(problems_csv, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            pid.append(int(row["id"]))
            problems.append({
                "id": int(row["id"]),
                "name": row["name"],
                "color": row["color"],
                "title": row["title"]
            })
    
    with open(teams_csv, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            teams.append({
                "id": int(row["id"]),
                "name": row["name"]
            })
    
    data = {
        "title": title,
        "systemName": "PDOGS",
        "systemVersion": "6.0",
        "problems": problems,
        "teams": teams
    }
    
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    
    print(f"CSV files '{problems_csv}' and '{teams_csv}' have been converted to JSON file '{json_file_path}'.")
    print("Please remember to copy the contest_data.json file to the ./js/contest_data.json.")
    edit_scoreboard(pid)
    

# Example usage
title = input("Please enter the contest title: ")
problem_csv = "ProblemsData.csv"
teams_csv = "TeamsData.csv"
csv_to_json(title, problem_csv, teams_csv, 'contest_data.json')