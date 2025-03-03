import csv
import json

def csv_to_json(title, problems_csv, teams_csv, json_file_path):
    problems = []
    teams = []
    
    with open(problems_csv, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
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
        "title": "PDAO 2025",
        "systemName": "PDOGS",
        "systemVersion": "6.0",
        "problems": problems,
        "teams": teams
    }
    
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    
    print(f"CSV files '{problems_csv}' and '{teams_csv}' have been converted to JSON file '{json_file_path}'.")
    print("Please remember to copy the contest_data.json file to the ./js/contest_data.json.")
    print("And remember to update the scoreboard problems set configuration via scoreboard_edit.sh!")

# Example usage
title = input("Please enter the contest title: ")
problem_csv = "ProblemsData.csv"
teams_csv = "TeamsData.csv"
csv_to_json(title, problem_csv, teams_csv, 'contest_data.json')