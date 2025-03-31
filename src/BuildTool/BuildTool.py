import os, csv, json, requests

if not os.path.exists("../credit"):
    os.makedirs("../credit")
def edit_scoreboard(sid, token, problems):
    print("Updating scoreboard ...")
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

def lazy_judge(flag, token, problem_id):
    if not flag:
        print("Lazy judge is disabling.")
        flag = False
    else:
        print("Lazy judge is enabling.")
        flag = True
    for i in problem_id:
        url = f"https://be.pdogs.ntu.im/problem/{i}"
        headers = {
            "auth-token": token,
            "Content-Type": "application/json"
        }
        data = {
            "is_lazy_judge": flag,
        }
        response = requests.patch(url, json=data, headers=headers)
        if response.status_code == 200:
            if response.json()["success"]:
                continue
            else:
                print(response.json()['error'])
                return
        else:
            print(f"Error occurred: {response.status_code}")
            return
    print("Lazy judge has been updated successfully.")


def csv_to_json(title, problems_csv, teams_csv, json_file_path, credit_path, sid_path):
    sid = input("Enter the scoreboard id from PDOGS: ")
    token = input("Enter the pdogs auth token: ")
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
    
    with open(teams_csv, mode='r', encoding='big5') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            teams.append({
                "id": int(row["id"]),
                "name": (row["name"].replace('(', '（').replace(')', '）') + " (" + row["school"] + ")"),
            })
    
    data = {
        "title": title,
        "systemName": "PDOGS",
        "systemVersion": "6.0",
        "problems": problems,
        "teams": teams
    }
    
    with open(sid_path, mode='w', encoding='utf-8') as sid_file:
        sid_file.write(sid)

    with open(credit_path, mode='w', encoding='utf-8') as toekn_file:
        toekn_file.write(token)

    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    
    print(f"Problems and Teams files have been converted to JSON file '{json_file_path}'.")
    print("Please check the data contest_data.json at ../contest_data.json.")
    edit_scoreboard(sid, token, pid)
    lazy_flag = input("Do you want to enable lazy judge? (y/n): ").strip().lower()
    if lazy_flag == 'y':
        lazy_judge(True, token, pid)
    else:
        lazy_judge(False, token, pid)
    

# Example usage
title = input("Please enter the contest title: ")
problem_csv = "ProblemsData.csv"
teams_csv = "TeamsData.csv"
csv_to_json(title, problem_csv, teams_csv, '../contest_data.json', '../credit/auth-token.txt', '../credit/sid.txt')
