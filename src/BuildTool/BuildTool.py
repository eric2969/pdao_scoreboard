import os, csv, json, requests

token = ""
sid = ""
problems = []
teams = []
pid = []

def Loading_Json(problems_csv, teams_csv):
    global problems, teams, pid
    if not os.path.exists(problems_csv) or not os.path.exists(teams_csv):
        print(f"Error: {problems_csv} or {teams_csv} not found.")
        return -1
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
    print("Problems and Teams data loaded successfully.")

def Create_ContestData():
    global problems, teams
    title = input("Please enter the contest title: ")
    print("Creating contest data ...")
    json_file_path = "../contest_data.json"
    data = {
        "title": title,
        "systemName": "PDOGS",
        "systemVersion": "6.0",
        "problems": problems,
        "teams": teams
    }
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    print(f"Problems and Teams files have been converted to JSON file '{json_file_path}'.")
    print("Please check the data contest_data.json at ../contest_data.json.")

def Create_CreditFiles():
    global token, sid
    if sid == "":
        sid = input("Enter the scoreboard id from PDOGS: ")
    if token == "":
        while True:
            token = input("Enter the auth-token from PDOGS: ").strip()
            url = f"https://be.pdogs.ntu.im/problem/1451"
            headers = {"auth-token": token, "Content-Type": "application/json"}
            response = requests.patch(url, headers=headers)
            if response.status_code == 200:
                if response.json()["error"] == "LoginExpired":
                    print("Invalid auth-token. Please enter a valid one.")
                    continue
                else:
                    break
            else:
                print(f"Error occurred when validating auth-token: {response.status_code}")
                return
    if not os.path.exists("../credit"):
        os.makedirs("../credit")
    sid_path = "../credit/sid.txt"
    token_path = "../credit/auth-token.txt"
    with open(sid_path, mode='w', encoding='utf-8') as sid_file:
        sid_file.write(sid)
    with open(token_path, mode='w', encoding='utf-8') as toekn_file:
        toekn_file.write(token)
    print("Credit files have been created successfully.")

def Edit_Scoreboard():
    global token, sid, pid
    if sid == "":
        sid = input("Enter the scoreboard id from PDOGS: ")
    if token == "":
        while True:
            token = input("Enter the auth-token from PDOGS: ").strip()
            url = f"https://be.pdogs.ntu.im/problem/1451"
            headers = {"auth-token": token, "Content-Type": "application/json"}
            response = requests.patch(url, headers=headers)
            if response.status_code == 200:
                if response.json()["error"] == "LoginExpired":
                    print("Invalid auth-token. Please enter a valid one.")
                    continue
                else:
                    break
            else:
                print(f"Error occurred when validating auth-token: {response.status_code}")
                return
    print("Updating scoreboard", sid, "...")
    url = f"https://be.pdogs.ntu.im/team-contest-scoreboard/{sid}"
    headers = {
        "auth-token": token,
        "Content-Type": "application/json"
    }
    data = {
        "challenge_label": "X",
        "title": "X",
        "target_problem_ids": pid,
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

def Edit_LazyJudge():
    global token, pid
    if token == "":
        while True:
            token = input("Enter the auth-token from PDOGS: ").strip()
            url = f"https://be.pdogs.ntu.im/problem/1451"
            headers = {"auth-token": token, "Content-Type": "application/json"}
            response = requests.patch(url, headers=headers)
            if response.status_code == 200:
                if response.json()["error"] == "LoginExpired":
                    print("Invalid auth-token. Please enter a valid one.")
                    continue
                else:
                    break
            else:
                print(f"Error occurred when validating auth-token: {response.status_code}")
                return
    while True:
        flag = input("Do you want to enable lazy judge? (y/n): ").strip().lower()
        if flag == 'y':
            print("Lazy judge is enabling.")
            flag = True
            break
        elif flag == 'n':
            print("Lazy judge is disabling.")
            flag = False
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
        
    for i in pid:
        url = f"https://be.pdogs.ntu.im/problem/{i}"
        headers = {
            "auth-token": token,
            "Content-Type": "application/json"
        }
        data = {
            "is_lazy_judge": flag,
            "judge_type": "NORMAL",
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

print("Welcome to the PDOGS scoreboard tool!\nLoading Problems and Teams data ...")
problem_csv = "ProblemsData.csv"
teams_csv = "TeamsData.csv"
if Loading_Json(problem_csv, teams_csv) == -1:
    print("Error loading data. Please check the CSV files.")
    exit(1)
while True:
    type = int(input("Menu:\n1. Complete Setup\n2. Create Scoreboard Contest File\n3. Create Backend Credit File\n4. Edit PDOGS Scoreboard Setting\n5. Edit Problems Lazy Judge Configuration\n6. Exit\nEnter your choice: "))
    if type == 1:
        Create_ContestData()
        Create_CreditFiles()
        Edit_Scoreboard()
        Edit_LazyJudge()
        print("Setup completed successfully.")
        print("Exiting the program.")
        break
    elif type == 2:
        Create_ContestData()
    elif type == 3:
        Create_CreditFiles()
    elif type == 4:
        Edit_Scoreboard()
    elif type == 5:
        Edit_LazyJudge()
    elif type == 6:
        print("Exiting the program.")
        break
    else:
        print("Invalid choice. Please try again.")
    print("")