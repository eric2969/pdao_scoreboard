import os, csv, json, requests, hashlib

sid = ""
headers = ""
problems = []
teams = []
pid = []

def Chk_Token():
    global headers
    if headers == "":
        while True:
            token = input("\nEnter the auth-token from PDOGS: ")
            if token == "":
                print("Auth-token cannot be empty. Please enter a valid one.")
                continue
            print("Validating auth-token ...")
            url = f"https://be.pdogs.ntu.im/problem/1451"
            headers_tmp = {"auth-token": token, "Content-Type": "application/json"}
            response = requests.patch(url, headers=headers_tmp)
            if response.status_code == 200:
                if response.json()["error"] == "LoginExpired":
                    print("Invalid auth-token. Please enter a valid one.")
                    continue
                else:
                    print("Auth-token is valid.")
                    headers = {"auth-token": token, "Content-Type": "application/json"}
                    break
            else:
                print(f"Error occurred when validating auth-token: {response.status_code}")
                return

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
    with open(teams_csv, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            teams.append({
                "id": int(row["id"]),
                "name": (row["name"].replace('(', '（').replace(')', '）') + " (" + row["school"] + ")"),
                "position": row["position"],
            })
    print("Problems and Teams data loaded successfully.")

def Create_ContestData():
    global problems, teams
    title = input("\nPlease enter the contest title: ")
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
    global headers, sid
    if sid == "":
        sid = input("\nEnter the scoreboard id from PDOGS: ")
    Chk_Token()
    if not os.path.exists("../credit"):
        os.makedirs("../credit")
    sid_path = "../credit/sid.txt"
    token_path = "../credit/auth-token.txt"
    with open(sid_path, mode='w', encoding='utf-8') as sid_file:
        sid_file.write(sid)
    with open(token_path, mode='w', encoding='utf-8') as toekn_file:
        toekn_file.write(headers["auth-token"])
    print("Credit files have been created successfully.")

def Set_Unlock_Token():
    while True:
        token = input("\nPlease enter the unlock token(length must in [8,20]): ")
        if len(token) < 8 or len(token) > 20:
            print("Unlock token length must be between 8 and 20 characters. Please enter a valid one.")
            continue
        break
    if not os.path.exists("../credit"):
        os.makedirs("../credit")
    Unlock_token_path = "../credit/Unlock-token.txt"
    lock_flag_path = "../credit/lock_flag.txt"
    hashed_token = hashlib.sha256(token.encode('utf-8')).hexdigest()
    with open(lock_flag_path, mode='w', encoding='utf-8') as lock_flag_file:
        lock_flag_file.write("true")
    os.chmod("../credit/lock_flag.txt", 0o777)
    with open(Unlock_token_path, mode='w', encoding='utf-8') as token_file:
        token_file.write(hashed_token)
    print("Unlock token has been created successfully, scoreboard has applied frozen lock.")

def Edit_Scoreboard():
    global headers, sid, pid
    if sid == "":
        sid = input("\nEnter the scoreboard id from PDOGS: ")
    Chk_Token()
    print("Updating scoreboard", sid, "...")
    url = f"https://be.pdogs.ntu.im/team-contest-scoreboard/{sid}"
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
    global headers, pid
    Chk_Token()
    while True:
        flag = input("\nDo you want to enable lazy judge? (y/n): ").strip().lower()
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
        print()
        print("Enablaing" if flag else "Disabling", "lazy judge for problem", i, "...")
        url = f"https://be.pdogs.ntu.im/problem/{i}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            if response.json()["success"]:
                judge_type = response.json()["data"]["judge_type"]
                if judge_type == "CUSTOMIZED":
                    print(f"Getting checker code of Problem {i}...")
                    checker_id = response.json()["data"]["judge_source"]["code_uuid"]
                    judge_url = "https://be.pdogs.ntu.im/s3-file/" + checker_id + "/url?filename=" + checker_id + "&as_attachment=true"
                    response = requests.get(judge_url, headers=headers)
                    if response.status_code == 200:
                        judge_source = response.json()["data"]["url"]
                    else:
                        print(f"Error occurred when get checker source: {response.status_code}")
                        return
                    judge_code = requests.get(judge_source)
                    if judge_code.status_code == 200:
                        judge_code = judge_code.text
                        print("Checker code fetched successfully.")
                    else:
                        print(f"Error occurred when get checker code: {judge_code.status_code}")
                        return
                    judge_source = {
                        "judge_language": "python 3.8",
                        "judge_code": judge_code,
                    }
                    data = {
                        "is_lazy_judge": flag,
                        "judge_type": judge_type,
                        "judge_source": judge_source,
                    }
                else:
                    data = {
                        "is_lazy_judge": flag,
                        "judge_type": judge_type,
                    }
                response = requests.patch(url, json=data, headers=headers)
                if response.status_code == 200:
                    if response.json()["success"]:
                        print(f"Lazy judge has been {'enabled' if flag else 'disabled'} for problem {i}.")
                        continue
                    else:
                        print(response.json()['error'])
                        return
                else:
                    print(f"Error occurred when updating lazy judge: {response.status_code}")
                    return
            else:
                print(response.json()['error'])
                return
        else:
            print(f"Error occurred when get judge type: {response.status_code}")
            return
    print("\nLazy judge has been updated successfully.")

print("Welcome to the PDOGS scoreboard tool!\nLoading Problems and Teams data ...")
problem_csv = "ProblemsData.csv"
teams_csv = "TeamsData_official.csv"
if Loading_Json(problem_csv, teams_csv) == -1:
    print("Error loading data. Please check the CSV files.")
    exit(1)
while True:
    type = int(input("\nMenu:\n1. Complete Setup\n2. Create Scoreboard Contest File\n3. Create Backend Credit File\n4. Edit PDOGS Scoreboard Setting\n5. Edit Problems Lazy Judge Configuration\n6. Set Scoreboard Frozen Lock\n7. Exit\nEnter your choice: "))
    if type == 1:
        Create_ContestData()
        Create_CreditFiles()
        Set_Unlock_Token()
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
        Set_Unlock_Token()
    elif type == 7:
        print("Exiting the program.")
        break
    else:
        print("Invalid choice. Please try again.")
