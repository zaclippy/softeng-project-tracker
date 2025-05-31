"""
For database management

Keynotes: There is an integrated testing suite which you can use to run the queries for the database.
Another thing is that we can now make any data in the backend accessible to the frontend by jsonifying out data and making it available at the given URLs.
There are now methods to grab certain data based upon a given selected project_id, employee_id, manager_id, etc. which will be given by the frontend using json.
This may also require that the frontend client stores the current employee_id that is currently accessing the page so that we can get the data specific for that employee.
The vast majority of POST and GET requests have been implemented, further, placeholder data along with some dummy data has been added to the database so that the frontend has something to work with.
The front end will only have to store the currently logged in employee_id, because with that we can access all projects, tasks, requirements, etc. that the employee is involved in.
It is not feasible to store the state of the logged in user in the backend because imagine trying to have a separate intance for the backend every time a user logs in, that would be a nightmare.
So it's better if we had a login system, or at least a way of keeping track of the currently logged in user in the frontend.

For anyone who wants to run the flask server(for a fresh install), you can do so by following these steps:
1.) chmod +x run.sh    (this makes the run.sh file executable)
2.) ./run.sh           (this runs the run.sh file and installs the dummy data into the database)
3.) comment out the line that says "insert_test_data()" in this file (800+ lines down) and uncomment the line that says "app.run(debug=True)"
4.) python3 databaseManipulator.py and now you can see the JSON'd data in your browser by going to http://127.0.0.1:5000/<insert path here> for example a path can be: http://127.0.0.1:5000/Requirement/Skills
(REMOVED) Honourable mention: you can run the testing suite by commenting out both lines after the previous steps and uncommenting the line that says "run_test_bed()"

INDEX BY LINE NUMBER:
    65  .) GET DATA REQUEST JSONs
    479 .) INSERT REQUEST JSONs
    683 .) DATABASE INSERT/UPDATE METHODS
    1082.) DATABASE RETRIEVAL METHODS
    1410.) MAIN FUNCTION

UPDATE: Rewrote the API endpoints to make it easier for Zach to use.

UPDATE: Replaced (most) arbitrary current project_id's with the current_project variable, also the same has been done with logged_in_employee_ID, this will make it easier for the frontend to use the API endpoints.
They can now update the current_project variable and the API endpoints will work with the current project that the user is looking at.
It's a global variable which kinda sucks, but we can do it based off of the assumption that the user will only be looking at one project at a time.

UPDATE: For safety reasons, I have removed the global connection variable and just declared a new connection variable in each method,
this is because having a global connection variable means that the connection will not be closed after each method call, which is bad.
I have also encapsulated each insert/get from database method into a try/except block
so that the backend doesn't just roll over and die every time there is a schema constraint error or something like that.
furthermore, in case there are no results for a given query, the method will return an empty list instead of None or something like 0 for phone numbers etc.,
this should help the frontend a lot because if a query has no results then the frontend will still have something to work with and won't just crash.

UPDATE: Initial Github API integration, I have added a method to get the code analysis data from the github API and I have added a method to insert the code analysis data into the database.
However, the predictions are just made up numbers as the ML part hasn't been integrated yet, so I just used random numbers for now.
I have also fixed the issue with the database data not having insert values for the github tokens, so now the database has the github tokens for each project.
The github repos in questions are my own personal projects, we should probably use github repos that have been updated recently so that the code analysis data is more accurate.
However, it works for now, method to change user has been implemented, can change current user using /ChangeEmployee

UPDATE: GANTT CHART ADDED TO FRONTEND, I have added a gantt chart to the frontend, I will try to make it look better later.
@author: Gerald
"""
from flask import Flask, request, jsonify # for API
import sqlite3 # for database management
from github import Github # for github API
import ast
from flask_cors import CORS # this is to allow CORS requests
from datetime import datetime # for getting the current date and time
from CodeAnalysis import getGitHubAnalysis # for getting the code analysis data from the github API
from initialAssessment import initialAnalysis
logged_in_employee_ID = 0 # this is the employee id of the currently logged in user, this will be used to get the data for the currently logged in user
current_project = 0 # project currently being looked at
app = Flask(__name__)
CORS(app) # just using for testing

# CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})

################################################################################################################################################################################################################################################
############################# GET REQUEST JSONs ################################################################################################################################################################################################
################################################################################################################################################################################################################################################

# For now, we will just return an aribtrary employees/managers data for each option because we haven't developed a login system for that yet.
# I rewrote some of this to make it easier for zach to use
# Made some more statistics to show on the dashboard

# Get data for Gantt chart
@app.route('/GanttChartData', methods=['GET', 'POST'])
def get_gantt_chart_json():
    project_id = current_project
    tasks = get_project_tasks(project_id)
    task_set = [] 
    today = datetime.today()
    if len(tasks) == 0:
        task_set = [{'Task': 'No tasks found for this project', 'Recommended task start': 0, 'Recommended start date': today.strftime("%d/%m/%Y"), "Recommended task duration (days)": 0}]
        response = {
            "length": 1,
            "list": task_set,
            "max": 0
        }
        return jsonify(response)
    if len(tasks) == 1:
        task_set = [{'Task': tasks[0]['task_name'], 'Recommended task start': 0, 'Recommended start date': today.strftime("%d/%m/%Y"), "Recommended task duration (days)": int((datetime.strptime(tasks[0]['task_deadline'], '%Y-%m-%d') - today).days)}]
        response = {
            "length": 1,
            "list": task_set,
            "max": 0
        }
        return jsonify(response)
    end = int((datetime.strptime(tasks[0]['task_deadline'], '%Y-%m-%d') - today).days)
    if (end > 0):
        task_set.append({'Task': tasks[0]['task_name'], 'Recommended task start': 0, 'Recommended start date': today.strftime("%d/%m/%Y"), "Recommended task duration (days)": end})
    for i in range(1, len(tasks)):
        start = int((datetime.strptime(tasks[i-1]['task_deadline'], '%Y-%m-%d') - today).days)
        end = int((datetime.strptime(tasks[i]['task_deadline'], '%Y-%m-%d') - today).days)
        if (end - start > 0):
            task_set.append({'Task': tasks[i]['task_name'], 'Recommended task start': start, 'Recommended start date': datetime.strptime(tasks[i-1]['task_deadline'], '%Y-%m-%d').strftime("%d/%m/%Y"), "Recommended task duration (days)": end - start})
    response = {
        "length": len(task_set),
        "list": task_set,
        "max": task_set[len(task_set) - 1]["Recommended task duration (days)"]
    }
    return jsonify(response)

# Get number of days before deadline
@app.route('/Project/Deadline', methods=['GET', 'POST'])
def get_project_deadline_json():
    project_id = current_project
    deadline = get_project_deadline(project_id)
    today = datetime.today()
    deadline = datetime.strptime(deadline, '%Y-%m-%d')
    days_left = deadline - today
    days_left = days_left.days
    response = {
        "days_left": days_left
    }
    return jsonify(response)

# Get the number of tasks that have been completed for a project
@app.route('/Project/CompletedTasks', methods=['GET', 'POST'])
def get_project_completed_tasks_json():
    project_id = current_project
    task_set = get_percentage_task_completed(project_id)
    total_number_of_employee_tasks = task_set[0]
    total_number_of_completed_tasks = task_set[1]
    percentage_task_completed = task_set[2]
    response = {
        "total_number_of_employee_tasks": total_number_of_employee_tasks,
        "total_number_of_completed_tasks": total_number_of_completed_tasks,
        "percentage_completed_tasks": percentage_task_completed
    }
    return jsonify(response)

# Get remaining budget for a project
@app.route('/Project/BudgetRemaining', methods=['GET', 'POST'])
def get_project_budget_json():
    project_id = current_project
    initial_budget = get_project_budget(project_id)
    list_of_requirements = get_project_requirements(project_id)
    total_cost = 0
    for t in list_of_requirements:
        total_cost += t['cost_to_fulfill']
    remaining_budget = initial_budget - total_cost
    response = {
        "initial_budget": initial_budget,
        "current_total_requirement_cost": total_cost,
        "remaining_budget": remaining_budget,
        "percentage_remaining_budget": (remaining_budget/initial_budget)*100
    }
    return jsonify(response)

# Get the number of employee skills that cover the requirements for a project, for example if a certain employee isn't available to fulfill a certain requirement then we might
# recommend that the project manager hire a new employee that has the required skills to fulfill the requirement.
@app.route('/Project/EmployeeSkills', methods=['GET', 'POST'])
def get_project_employee_skills_json():
    global current_project
    project_id = current_project
    list_of_requirements = get_project_requirements(project_id) 
    list_of_requirement_ids = []
    list_of_required_skills_id = set()
    list_of_required_skills = set()
    for t in list_of_requirements:
        list_of_requirement_ids.append(t['requirement_id'])
    for id in list_of_requirement_ids:
        for skill in get_skill_for_requirement(id):
            list_of_required_skills_id.add(skill['skill_id'])
            list_of_required_skills.add(skill['skill_title'])
    list_of_project_members = get_project_members(project_id)
    list_of_project_member_ids = []
    for t in list_of_project_members:
        list_of_project_member_ids.append(t['employee_id'])
    list_of_project_member_skills_id = set()
    list_of_project_member_skills = set()
    for id in list_of_project_member_ids:
        for skill in get_skill_for_employee(id):
            list_of_project_member_skills_id.add(skill['skill_id'])
            list_of_project_member_skills.add(skill['skill_name'])
    number_of_skills_covered = 0
    missing_skill_id = []
    for skill in list_of_required_skills_id:
        if skill in list_of_project_member_skills_id:
            number_of_skills_covered += 1
        else:
            missing_skill_id.append(skill)
    list_skills = []
    list_employee_with_skills = []
    if not missing_skill_id:
        missing_skill_id = ["All skills covered"]
        list_skills = ["All skills covered"]
        list_employee_with_skills = ["All skills covered"]
    else:
        for skill in missing_skill_id:
            list_skills.append(get_skill_name_from_id(skill))
            list_employee_with_skills.append(get_all_employees_with_skill(skill))
    if len(list_of_required_skills) == 0:
        percentage_of_skills_covered = 100
    else:
        percentage_of_skills_covered = (number_of_skills_covered/len(list_of_required_skills))*100

    response = {
        "list_of_required_skills":         list(list_of_required_skills),
        "list_of_project_member_skills":   list(list_of_project_member_skills),
        "total_number_of_employee_skills": len(list_of_project_member_skills),
        "number_of_skills_covered":        number_of_skills_covered,
        "number_of_required_skills":       len(list_of_required_skills),
        "percentage_of_skills_covered":    percentage_of_skills_covered,
        "missing_skills":                  list_skills,
        "employees_with_missing_skills":   list_employee_with_skills
    }
    return jsonify(response)

# Get all skills in database for API endpoint
@app.route('/Skills/All', methods=['GET'])
def get_all_skills_json():
    skills = get_all_skills()
    response = {
        "list": skills
    }
    return jsonify(response)

# Define an API endpoint for retrieving all employees
@app.route('/Employees/All', methods=['GET'])
def get_all_employees_json():
    employees = get_all_employees()
    response = {
        "list": employees
    }
    return jsonify(response)

# Define an API endpoint for only retrieving all project team members
@app.route('/Employees/OnProject', methods=['GET', 'POST'])
def get_all_employees_on_project_json():
    # project_id = request.json['project_id']
    project_id = current_project
    response = get_project_members(project_id) # have to know what project we are getting employees for which requires the frontend to store the project id currently being looked at we just have 3 (4) for now
    # response = {"list": members}
    return jsonify(response)

# Define an API endpoint for displaying everything on the Team page - project team members and projects managed
@app.route('/Employees/Team', methods=['GET', 'POST'])
def get_employees_team_json():
    project_id = current_project
    members = get_project_members(project_id)
    response = {
        "project_name" : get_project_name(project_id), 
        "list": members
    }
    return jsonify(response)

# Define an API endpoint for retrieving all tasks for a team member
@app.route('/Employees/Tasks', methods=['GET', 'POST'])
def get_all_tasks_for_employee_json():
    # employee_id = request.json['employee_id']
    employee_id = logged_in_employee_ID
    tasks = get_tasks_for_member(employee_id)
    response = {
        "employee_name": get_employee_name(employee_id),
        "list": tasks
    }
    return jsonify(response)

# Define an API endpoint for retrieving all skills for a team member (should depend on what employee they click on)
@app.route('/Employees/Skills', methods=['GET', 'POST'])
def get_all_skills_for_employee_json():
    data = request.get_json()
    employee_id = data['employee_id']
    skills = get_skill_for_employee(employee_id)
    name = get_employee_name(employee_id)
    main_skill = get_main_skill_for_employee(employee_id)
    response = {
        "employee_name": name,
        "main_skill":    main_skill,
        "list":          skills
    }
    return jsonify(response)

# Define an API endpoint for retrieving all projects for a specific manager
@app.route('/Manager/Projects', methods=['GET', 'POST'])
def get_all_projects_for_manager_json():
    manager_id = logged_in_employee_ID
    response = get_project_from_manager(manager_id)
    return jsonify(response)

# Define an API endpoint for retrieving all requirements for a specific project
@app.route('/Project/Requirements', methods=['GET', 'POST'])
def get_all_requirements_for_project_json():
    project_id = current_project
    requirements = get_project_requirements(project_id)
    response = {
        "project_name" : get_project_name(project_id), 
        "list": requirements
    }
    return jsonify(response)

# Define an API endpoint for retrieving all tasks for a specific project
@app.route('/Project/Tasks', methods=['GET', 'POST'])
def get_all_tasks_for_project_json():
    project_id = current_project
    tasks = get_project_tasks(project_id)
    response = {
        "project_name" : get_project_name(project_id), 
        "list": tasks
    }
    return jsonify(response)

# im making a new one to edit it for the frontend
@app.route('/Project/TasksDisplay', methods=['GET', 'POST'])
def taskdisplay():
    # project_id = request.json['project_id']
    project_id = current_project
    tasks_list = get_project_tasks(project_id)
    response = {
        "project_name" : get_project_name(project_id), 
        "list":[{
            "id": t["task_id"],
            "name":        t["task_name"],
            "finished":    t["finished"],
            "deadline":    t["task_deadline"],
            "description": t["task_description"]
        } for t in tasks_list]
    }
    return jsonify(response)


# Define an API endpoint for getting all requests for a manager
@app.route('/Manager/Requests', methods=['GET', 'POST'])
def get_all_requests_for_manager_json():
    manager_id = logged_in_employee_ID
    requests = get_request_for_project_manager(manager_id)
    response = {
        "manager_name": get_employee_name(manager_id),
        "list": requests
    }
    return jsonify(response)

# Define an API endpoint for getting all requests for a team member
@app.route('/Employee/Requests', methods=['GET', 'POST'])
def get_all_requests_for_employee_json():
    employee_id = logged_in_employee_ID
    request_list = get_request_for_employee(employee_id)
    response = {
        "employee_name": get_employee_name(employee_id),
        "list":          request_list
    }
    return jsonify(response)

# Define an API endpoint for getting an employee's details
@app.route('/Employee/Details', methods=['GET', 'POST'])
def get_employee_details_json():
    #data = request.get_json()
    employee_id = 4#data['employee_id']
    employee_details = get_employee_details(employee_id)[0]
    response = {
            'first_name':   employee_details['first_name'],
            'last_name':    employee_details['last_name'],
            'email':        employee_details['email'],
            'phone_number': employee_details['phone_number']
    }
    return jsonify(response)

# Define an API endpoint for getting information for a manager
@app.route('/Manager/Details', methods=['GET', 'POST'])
def get_manager_details_json():
    # manager_id = request.json['manager_id']
    manager_id = logged_in_employee_ID
    manager_deets = get_project_manager_details(manager_id)[0]
    response = {
            'first_name':   manager_deets['first_name'],
            'last_name':    manager_deets['last_name'],
            'email':        manager_deets['email'],
            'phone_number': manager_deets['phone_number']
        }
    return jsonify(response)

# Define an API endpoint for getting all skills for a requirement
@app.route('/Requirement/Skills', methods=['GET', 'POST'])
def get_all_skills_for_requirement_json():
    # data = request.get_json()
    requirement_id = 77777
    response = get_skill_for_requirement(requirement_id)
    return jsonify(response)


@app.route('/HeaderData', methods=['GET', 'POST'])
def header_data():
    manager = get_project_manager_details(logged_in_employee_ID)[0]
    username = manager['first_name'] +  " " + manager['last_name']
    data = {
        'username': username,
        'manager': True
    } 
    response= jsonify(data)
    return response

# here is where all the statistics shown on the dashboard go
@app.route('/DashboardData', methods=['GET', 'POST'])
def get_data():
    # data = request.get_json()
    # managerID = 0
    all_projects = get_project_from_manager(logged_in_employee_ID) # gets the dictionaries of the manager's projects
    project = get_project_from_id(current_project) # should be changed by switch project
    project_id = project[0]
    project_name = project[2] # fixed this, now it gets from database
    deadline = project[3]
    budget = get_project_budget(project_id)
    readiness = get_project_readiness(project_id)
    code_quality = 6
    initial_budget = get_project_budget(project_id)
    list_of_requirements = get_project_requirements(project_id)
    total_cost = 0
    today = datetime.today()
    deadline = deadline[:10]
    remaining = (datetime.strptime(deadline, '%Y-%m-%d') - today).days
    for t in list_of_requirements:
        total_cost += t['cost_to_fulfill']
    remaining_budget = initial_budget - total_cost
    data = {
        'project_name':     project_name,
        'switch_projects':  [p['project_title'] for p in all_projects],
        'deadline':         datetime.strptime(deadline, '%Y-%m-%d').strftime("%d/%m/%Y"),
        'remaining_days':   remaining, 
        'risk':             6,
        'readiness':        round(readiness, 0), # can now pass correct value based on what project the user is looking at but project_id is hardcoded for testing
        'budget':           budget, 
        'remaining_budget': remaining_budget,
    } 
    response= jsonify(data)
    return response

# doing the github data separately because it takes a while to load
@app.route('/GitData', methods=['GET', 'POST'])
def gitData():
    git_analysis = get_github_analysis()
    data = {
        'code': git_analysis,
    } 
    response= jsonify(data)
    return response

# doing the risk and cocomo data separately because it also takes a while to load
@app.route('/Estimates', methods=['GET', 'POST'])
def estimates():
    git_risk = get_github_analysis()
    estimates_data = get_estimates(current_project)['advice']
    response =  { 
        'project_risk' : str(int((float(estimates_data[10].strip('%'))/5)*3) + ((float(git_risk[8])/5) * 2)),
        'estimates':
    [[
         "Time estimation:",
         str(estimates_data[2]) + ("month" if estimates_data[2] == 1 else " months"),
         estimates_data[6]
    ],
    [
         "Cost estimation:" ,
         "£" + str(estimates_data[3]),
         estimates_data[7]
    ],
    [
         "Required manpower estimation: "  ,
         str(estimates_data[5]),
         estimates_data[8]
    ],
    [
         "Lines of code estimation: ",
         "",
         estimates_data[9]
    ]],
    }

    return jsonify(response)

################################################################################################################################################################################################################################################
##################################### INSERT OR UPDATE (POST) JSONs ############################################################################################################################################################################
################################################################################################################################################################################################################################################

#Define an API endpoint for updating what project we're looking at
@app.route('/ChangeProject', methods=['POST'])
def change_project():
    data = request.get_json()
    project_name = data['project_name']
    global current_project
    current_project = get_project_id_from_name(project_name)
    return jsonify({'project': current_project})

# Define an API endpoint for accessing the site from a new employees point of view
@app.route('/ChangeEmployee', methods=['POST'])
def change_employee():
    data = request.get_json()
    global logged_in_employee_ID
    employee_id = data['id']
    employee_email = data['email']
    print(employee_id), employee_email
    if (check_if_user_exists(employee_email, employee_id) == False):
        print("unsuccessful login")
        return jsonify({'employee_id': logged_in_employee_ID})
    logged_in_employee_ID = employee_id
    # now switch to the correct project
    project_id = get_project_from_manager(employee_id)[0]
    return jsonify({'employee_id': logged_in_employee_ID})

# Define an API endpoint for adding a new employee (for non-managers) none of these methods work unless the frontend passes back data to these so don't try http://127.0.0.1:5000/AddEmployee
@app.route('/AddEmployee', methods=['GET', 'POST'])
def add_project_team_member_json():
    data = request.get_json()
    first_name = data['first_name'] 
    last_name = data['last_name']   
    email = data['email']
    phone_number = data['phone_number']
    add_employee(first_name, last_name, email, phone_number)
    return jsonify({'message': 'Member added successfully'})

# For adding managers, a database manger must do this
@app.route('/AddManager', methods=['POST'])
def add_project_manager_json():
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    phone_number = data['phone_number']
    github_token = data['github_token']
    add_project_manager(first_name, last_name, email, phone_number, github_token)
    return jsonify({'message': 'Member added successfully'})

# Define an API endpoint for a manger to insert an employee into a project
@app.route('/AssignEmployee', methods=['POST'])
def assign_project_team_member_to_project_json():
    data = request.get_json()
    employee_id  = data['employee_id']
    project_id   = data['project_id']
    project_role = data['project_role']
    assign_project_team_member_to_project(employee_id, project_id, project_role)
    return jsonify({'message': 'Member assigned successfully'})

# Define an API endpoint for unassigning an employee from a project and adding them to the placeholder project marked 'UNASSIGNED'
@app.route('/UnassignEmployee', methods=['POST'])
def unassign_project_team_member_from_project_json():
    data = request.get_json()
    employee_id = data['employee_id']
    assign_project_team_member_to_project(employee_id, 999, 'UNASSIGNED')
    return jsonify({'message': 'Member unassigned successfully'})

# Define API endpoint project managers to make new projects
@app.route('/AddProject', methods=['GET', 'POST'])
def add_project_json():
    data = request.get_json()
    project_title = data['projectName']
    project_deadline = data['deadline']
    project_budget = data['budget']
    client_name = data['projectClientName']
    project_type = data['projectType']
    cocomo_data = data['cocomoInputs']
    # here is the cocomo bit:
    cocomo = insert_new_project_with_estimate(project_title, project_deadline, client_name, project_type, cocomo_data[0], cocomo_data[1],  project_budget, cocomo_data[4], cocomo_data[5], cocomo_data[6], cocomo_data[7], cocomo_data[8], cocomo_data[9], cocomo_data[10], cocomo_data[11], cocomo_data[12], cocomo_data[13])
    return jsonify({'cocomo': cocomo})

# Define API endpoint for project managers to create requirements for projects
@app.route('/AddRequirement', methods=['POST'])
def add_requirement_json():
    data = request.get_json()
    project_id = current_project
    requirement_title = data['requirement_title']
    requirement_priority = data['project_priority_level']
    core_feature = data['core_feature']
    cost_to_fulfill = data['cost_to_fulfill']
    add_project_requirement(project_id, requirement_title, requirement_priority, core_feature, cost_to_fulfill)
    return jsonify({'message': 'Requirement added successfully'})

# Define API endpoint for project managers to create tasks for Requirements
@app.route('/AddTask', methods=['POST'])
def add_task_json():
    data = request.get_json()
    requirement_id = data['requirementID']
    task_title = data['name']
    task_deadline = datetime.fromisoformat(data['deadline'][:-1] + '+00:00').strftime('%Y-%m-%d') # now in the format required by sqlite
    task_description = data['description']
    add_project_task(requirement_id, task_title, task_deadline, task_description)
    return jsonify({'message': 'Task added successfully'})

# Define API endpoint for project managers to assign tasks to employees
@app.route('/AssignTask', methods=['POST'])
def assign_task_json():
    data = request.get_json()
    task_id = data['task_id']
    employee_id = data['employee_id']
    add_employee_task(employee_id, task_id)
    return jsonify({'message': 'Task assigned successfully'})

# Define API endpoint for a user to complete a task
@app.route('/CompleteTask', methods=['POST'])
def complete_task_json():
    data = request.get_json()
    task_id = data['task_id']
    employee_id = logged_in_employee_ID
    update_task_finished(task_id, employee_id)
    return jsonify({'message': 'Task completed successfully'})

# Define API endpoint for a database admin to add a new company skill to the database
@app.route('/AddSkill', methods=['POST'])
def add_skill_json():
    data = request.get_json()
    skill_name = data['skill_name']
    skill_description = data['skill_description']
    add_skill(skill_name, skill_description)
    return jsonify({'message': 'Skill added successfully'})

# Define API endpoint for a project manager to add a new skill required to fulfill a requirement
@app.route('/AddRequirementSkill', methods=['POST'])
def add_requirement_skill_json():
    data = request.get_json()
    requirement_id = data['requirement_id']
    skill_id = data['skill_id']
    add_skill_requirements(skill_id, requirement_id)
    return jsonify({'message': 'Requirement skill added successfully'})

# Define API endpoint for an employee to add a new skill to their profile
@app.route('/AddEmployeeSkill', methods=['POST'])
def add_employee_skill_json():
    data = request.get_json()
    employee_id = logged_in_employee_ID
    skill_id = data['skill_id']
    main_skill = data['main_skill']
    add_employee_skill(employee_id, skill_id, main_skill)
    return jsonify({'message': 'Employee skill added successfully'})

# Define API endpoint for a member to send a manager a request
@app.route('/AddRequest', methods=['POST'])
def add_request_json():
    data = request.get_json()
    manager_id = data['manager_id']
    request_title = data['request_title']
    request_description = data['request_description']
    add_member_request(manager_id, logged_in_employee_ID, request_title, request_description)
    return jsonify({'message': 'Request added successfully'})

# Define API endpoint for a manager to fulfill a request
@app.route('/FulfillRequest', methods=['POST'])
def fulfill_request_json():
    data = request.get_json()
    request_id = data['request_id']
    update_request_fulfilled(request_id)
    return jsonify({'message': 'Request fulfilled successfully'})

# Define API endpoint for a team member to update a task's completion status
@app.route('/UpdateTaskCompletion', methods=['POST'])
def update_task_completion_json():
    data = request.get_json()
    task_id = data['task_id']
    update_task_finished(task_id, logged_in_employee_ID)
    return jsonify({'message': 'Task completion status updated successfully'})

# Define API endpoint for a manager to update a requirements cost to fulfill
@app.route('/UpdateRequirementCost', methods=['POST'])
def update_requirement_cost_json():
    data = request.get_json()
    requirement_id = data['requirement_id']
    cost_to_fulfill = data['cost_to_fulfill']
    update_requirement_cost(requirement_id, cost_to_fulfill)
    return jsonify({'message': 'Requirement cost updated successfully'})

# Define API endpoint for a member to update their main skill
@app.route('/UpdateMainSkill', methods=['POST'])
def update_main_skill_json():
    data = request.get_json()
    employee_id = logged_in_employee_ID
    skill_id = data['skill_id']
    update_skill_main(employee_id, skill_id)
    return jsonify({'message': 'Main skill updated successfully'})




################################################################################################################################################################################################################################################
##################################### INSERT/UPDATE STUFF TO DATABASE ##########################################################################################################################################################################
################################################################################################################################################################################################################################################

# these functions should be self explanatory based on the SQL statements
# functions with the suffix _specified_id are for when the user wants to specify the id of the employee they are adding and are only for the insert_test_data function below (line 671)

# YOU GET A TRY/EXCEPT BLOCK
def add_project_team_member_specified_id(id, first_name, last_name, email, phone_number, project_id, project_role):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('INSERT INTO employee (employee_id, first_name, last_name, email, phone_number) values (?, ?, ?, ?, ?)', (id, first_name, last_name, email, phone_number))
        conn.execute('INSERT INTO project_team_member (employee_id, project_id, project_role) values (?, ?, ?)', (id, project_id, project_role))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

# YOU GET A TRY/EXCEPT BLOCK
def add_employee(first_name, last_name, email, phone_number):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.cursor()
        cursor = conn.execute('INSERT INTO employee (first_name, last_name, email, phone_number) values (?, ?, ?, ?)', (first_name, last_name, email, phone_number))
        conn.execute('INSERT INTO project_team_member (employee_id, project_id, project_role) values (?, ?, ?)', (cursor.lastrowid, 999, "UNASSIGNED"))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

# EVERYBODY GETS A TRY/EXCEPT BLOCK!!!!!!!!!!!!111
def assign_project_team_member_to_project(employee_id, project_id, project_role):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('UPDATE project_team_member SET project_id=?, project_role=? WHERE employee_id=?', (project_id, project_role, employee_id))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

def add_project_manager_specified_id(id, first_name, last_name, email, phone_number, github_token):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('INSERT INTO employee (employee_id, first_name, last_name, email, phone_number) values (?, ?, ?, ?, ?)', (id, first_name, last_name, email, phone_number))
        conn.execute('INSERT INTO project_manager (employee_id, first_name, last_name, email, phone_number, github_token) values (?, ?, ?, ?, ?, ?)', (id, first_name, last_name, email, phone_number, github_token))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

def add_project_manager(first_name, last_name, email, phone_number, github_token):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('INSERT INTO employee (first_name, last_name, email, phone_number) values (?, ?, ?, ?)', (first_name, last_name, email, phone_number))
        conn.execute('INSERT INTO project_manager (first_name, last_name, email, phone_number, github_token) values (?, ?, ?, ?, ?)', (first_name, last_name, email, phone_number, github_token))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

def insert_new_project_specified_id(manager_id, project_id, project_title, project_deadline, project_budget, client_name, project_type, github_token):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cocomo = github_token
        conn.execute('INSERT INTO project (manager_id, project_id, project_title, project_deadline, project_budget, client_name, project_type, github_token) values (?, ?, ?, ?, ?, ?, ?, ?)', (manager_id, project_id,  project_title, project_deadline, project_budget, client_name, project_type, github_token))
        if (project_id == 0):
            conn.execute('INSERT INTO estimates (project_id, thousand_lines_of_code, completion_months_est, spent_money_est, advice) values (?, ?, ?, ?, ?)', (project_id, 2, 10, 9999, "['121.23', '10000', '24', '30000.00', '50', '17', 'With the current setup this project is expected to take: 24 months. This is 11 months past the deadline!', 'WARNING: This project is underfunded. Recommended Budget change:  +£10000.00. This is +50.00%', 'WARNING: There are not enough people assigned to this project! To complete the project in 5.67 months, the team size should be increased to 17', 'The productivity required on this project is 14.31 thousand lines of code per month', '100%']"))
        elif (project_id == 1):
            conn.execute('INSERT INTO estimates (project_id, thousand_lines_of_code, completion_months_est, spent_money_est, advice) values (?, ?, ?, ?, ?)', (project_id, 2, 10, 9999, "['136.92', '11000', '69', '11000.00', '10', '11', 'With the current setup this project is expected to take: 69 months. This is 11 months past the deadline!', 'WARNING: This project is underfunded. Recommended Budget change:  +£1000.00. This is +10.00%', 'WARNING: There are not enough people assigned to this project! To complete the project in 57.86 months, the team size should be increased to 11', 'The productivity required on this project is 3.27 thousand lines of code per month', '100%']"))
        elif (project_id == 1000):
            conn.execute('INSERT INTO estimates (project_id, thousand_lines_of_code, completion_months_est, spent_money_est, advice) values (?, ?, ?, ?, ?)', (project_id, 2, 10, 9999, "['134.21', '5000', '86', '40000.00', '14', '22', 'With the current setup this project is expected to take: 86 months. This is 1 month past the deadline!', 'WARNING: This project is underfunded. Recommended Budget change:  +£1000.00. This is +14.29%', 'WARNING: There are not enough people assigned to this project! To complete the project in 84.20 months, the team size should be increased to 22', 'The productivity required on this project is 20.89 thousand lines of code per month', '100%']"))
        else:
            conn.execute('INSERT INTO estimates (project_id, thousand_lines_of_code, completion_months_est, spent_money_est, advice) values (?, ?, ?, ?, ?)', (project_id, 2, 10, 9999, "['134.21', '40000', '86', '5000.00', '14', '22', 'With the current setup this project is expected to take: 86 months. This is 1 month past the deadline!', 'WARNING: This project is underfunded. Recommended Budget change:  +£1000.00. This is +14.29%', 'WARNING: There are not enough people assigned to this project! To complete the project in 84.20 months, the team size should be increased to 22', 'The productivity required on this project is 20.89 thousand lines of code per month', '100%']"))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False
    
# to add new projects
def insert_new_project_with_estimate(  project_title, project_deadline, client_name, project_type 
                                     , team_size, monthly_salary, budget, requirements, RS, SD
                                     , complexity, experience, PL, ST, DS
                                     , LOC_0, LOC_1):
    try:
        #input [teamSize, monthlySalary, budget, deadline, requirements, RS, SD, complexity, experience, PL, ST, DS, LOC, LOC2]
        analysisResult = initialAnalysis([team_size, monthly_salary, budget, project_deadline
                                          , requirements, RS, SD
                                          , complexity, experience, PL, ST, DS
                                          , LOC_0, LOC_1]) 
                                                           
        #output format - [KSLOC, cost, predictedTime, budgetC, budgetPC, requiredTeam, Deadline information, Budget information, team changes, productivity]
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        github_token = get_project_manager_details(logged_in_employee_ID)[0]['github_token']
        token = Github(github_token)
        user = token.get_user()
        repo = user.create_repo(project_title)
        file = 'HelloGroup34.java'
        repo.create_file(file, "Your first commit!", "There is nothing here yet... maybe someone will add something soon?")
        KSLOC = analysisResult[0]
        completion_months_est = analysisResult[2]
        spent_money_est = analysisResult[1]
        strip_project_deadline = project_deadline[:10]
        fixed_project_deadline = datetime.strptime(strip_project_deadline, '%Y-%m-%d')
        cursor = conn.execute('INSERT INTO project (manager_id, project_title, project_deadline, project_budget, client_name, project_type, github_token) values (?, ?, ?, ?, ?, ?, ?)', (logged_in_employee_ID, project_title, fixed_project_deadline, budget, client_name, project_type, github_token))
        conn.execute('INSERT INTO estimates (project_id, thousand_lines_of_code, completion_months_est, spent_money_est, project_risk, advice) values (?, ?, ?, ?, ?, ?)', (cursor.lastrowid, KSLOC, completion_months_est, spent_money_est, 10, str(analysisResult)))
        conn.commit()
        conn.close()
        return analysisResult
    except sqlite3.IntegrityError:
        return [0, 0, 0, 0, 0, 0, "error", "error", "error", "error"]

def add_project_requirement_specified_id(id, project_id, requirement_title, project_priority_level, core_feature, cost_to_fulfill):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('INSERT INTO requirement (requirement_id, project_id, requirement_title, project_priority_level, core_feature, requirement_fulfilled, cost_to_fulfill) values (?, ?, ?, ?, ?, ?, ?)', (id, project_id, requirement_title, project_priority_level, core_feature, 0,  cost_to_fulfill))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

def add_project_requirement(project_id, requirement_title, project_priority_level, core_feature, cost_to_fulfill):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('INSERT INTO requirement (project_id, requirement_title, project_priority_level, core_feature, requirement_fulfilled, cost_to_fulfill) values (?, ?, ?, ?, ?, ?)', (project_id, requirement_title, project_priority_level, core_feature, 0,  cost_to_fulfill))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

def add_project_task_specified_id(task_id, fulfill_requirement_id, task_name, task_deadline, task_description):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('INSERT INTO task (task_id, subtask_dependency_id, fulfill_requirement_id, task_name, finished, task_deadline, task_description) values (?, ?, ?, ?, ?, ?, ?)', (task_id, 0, fulfill_requirement_id, task_name, 0, task_deadline, task_description))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False
    
def add_project_task(fulfill_requirement_id, task_name, task_deadline, task_description):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('INSERT INTO task (subtask_dependency_id, fulfill_requirement_id, task_name, finished, task_deadline, task_description) values (?, ?, ?, ?, ?, ?)', (0, fulfill_requirement_id, task_name, 0, task_deadline, task_description))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False
def add_employee_task(employee_id, task_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('INSERT INTO employee_task (employee_id, task_id, employee_finished) values (?, ?, ?)', (employee_id, task_id, 0))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

def add_skill_specified_id(skill_id, skill_name, skill_description):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('INSERT INTO skill (skill_id, skill_title, skill_description) values (?, ?, ?)', (skill_id, skill_name, skill_description))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

def add_skill(skill_name, skill_description):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('INSERT INTO skill (skill_title, skill_description) values (?, ?)', (skill_name, skill_description))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

def add_skill_requirements(skill_id, requirement_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('INSERT INTO skill_requirement (skill_id, requirement_id) values (?, ?)', (skill_id, requirement_id))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

def add_employee_skill(employee_id, skill_id, main_skill):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT COUNT(*) FROM employee_skill WHERE skill_main=1 AND employee_id=?;', (employee_id,))
        count = cursor.fetchone()[0]
        if (count > 0 and main_skill == 1):
            return
        conn.execute('INSERT INTO employee_skill (employee_id, skill_id, skill_main) values (?, ?, ?)', (employee_id, skill_id, main_skill))
        conn.commit()
    except sqlite3.IntegrityError:
        return False

# If an employee doesn't have a main skill yet but wants to set one 
def update_skill_main(employee_id, skill_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT COUNT(*) FROM employee_skill WHERE skill_main=1 AND employee_id=?;', (employee_id,))
        count = cursor.fetchone()[0]
        if (count > 0):
            return
        conn.execute('UPDATE employee_skill SET skill_main=1 WHERE employee_id=? AND skill_id=?;', (employee_id, skill_id))
        conn.commit()
    except sqlite3.IntegrityError:
        return False


def add_member_request(manager_id, member_id, request, request_date, request_fulfilled):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('INSERT INTO member_request (manager_id, member_id, request, request_date, request_fulfilled) values (?, ?, ?, ?, ?)', (manager_id, member_id, request, request_date, request_fulfilled))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

def update_request_fulfilled(request_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('UPDATE member_request SET request_fulfilled=1 WHERE request_id=?;', (request_id,))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

def update_requirement_fulfilled(requirement_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('UPDATE requirement SET requirement_fulfilled=1 WHERE requirement_id=?;', (requirement_id,))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

# Cascading update fulfillment of task and requirement, if all employees finish a task then the task in the task table is finished, once all tasks for a requirement are finished then the requirement is fulfilled
def update_task_finished(task_id, employee_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('UPDATE employee_task SET employee_finished=1 WHERE task_id=? AND employee_id=?;', (task_id, employee_id))
        conn.commit()
        cursor = conn.execute('SELECT COUNT(*) FROM employee_task WHERE task_id=? AND employee_finished=0;', (task_id,))
        count = cursor.fetchone()[0]
        if (count == 0):
            conn.execute('UPDATE task SET finished=1 WHERE task_id=?;', (task_id,))
            conn.commit()
        requirement_fulfilled_for_task = conn.execute('SELECT fulfill_requirement_id FROM task WHERE task_id=?;', (task_id,)).fetchone()[0]
        cursor = conn.execute('SELECT COUNT(*) FROM task WHERE fulfill_requirement_id=? AND finished=0;', (requirement_fulfilled_for_task,))
        count = cursor.fetchone()[0]
        if (count == 0):
            conn.execute('UPDATE requirement SET requirement_fulfilled=1 WHERE requirement_id=?;', (requirement_fulfilled_for_task,))
            conn.commit()
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

def update_requirement_cost(requirement_id, cost):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        conn.execute('UPDATE requirement SET cost_to_fulfill=? WHERE requirement_id=?;', (cost, requirement_id))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return False

################################################################################################################################################################################################################################################
##################################### GET STUFF FROM DATABASE (NOT JSONIFIED) TEST EDITION #####################################################################################################################################################
################################################################################################################################################################################################################################################

def get_project_members_test():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)            
        project_id = int(input("Input project id:"))
        cursor = conn.execute('SELECT * FROM get_employee_on_project WHERE project_id=?;', (project_id,))
        for row in cursor:
            print({'employee_id': row[0], 'first_name': row[1], 'last_name': row[2], 'email': row[3], 'phone': row[4], 'role': row[5]})
        conn.close()
    except sqlite3.IntegrityError:
        print("Error get project members")

def get_project_from_manager_test():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        manager_id = int(input("Input manager id:"))
        cursor = conn.execute('SELECT * FROM project WHERE manager_id=?;', (manager_id,))
        for row in cursor:
            print({'project_id': row[0], 'manager_id': row[1], 'project_title': row[2], 'project_deadline': row[3], 'project_budget': row[4], 'client_name': row[5], 'project_type': row[6]})
        conn.close()
    except sqlite3.IntegrityError:
        print("Error get project from manager")

def get_all_employees_test():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)  
        cursor = conn.execute('SELECT * FROM employee')
        for row in cursor:
            print({'employee_id': row[0], 'email': row[1], 'first_name': row[2], 'last_name': row[3], 'phone': row[4]})
        conn.close()
    except sqlite3.IntegrityError:
        print("Error get all employees")

def get_project_budget_test():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)      
        project_id = int(input("Input project id:"))
        cursor = conn.execute('SELECT project_budget from project WHERE project_id=?;', (project_id,))
        for row in cursor:
            print({'project_budget': row[0]})
        conn.close()
    except sqlite3.IntegrityError:
        print("Error get project budget")

def get_project_requirements_test():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        project_id = int(input("Input project id:"))
        cursor = conn.execute('SELECT * FROM requirement WHERE project_id=?;', (project_id,))
        for row in cursor:
            print({'requirement_id': row[0], 'project_id': row[1], 'requirement_title': row[2], 'project_priority_level': row[3], 'core_feature': row[4], 'requirement_fulfilled': row[5], 'cost_to_fulfill': row[6]})
        conn.close()
    except sqlite3.IntegrityError:
        print("Error get project requirements")

def get_project_tasks_test():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        project_id = int(input("Input project id:"))
        cursor = conn.execute('SELECT * FROM task WHERE fulfill_requirement_id IN (SELECT requirement_id FROM requirement WHERE project_id=?);', (project_id,))
        for row in cursor:
            print({'task_id': row[0], 'subtask_dependency_id': row[1], 'fulfill_requirement_id': row[2], 'task_name': row[3], 'finished': row[4], 'task_deadline': row[5], 'task_description': row[6]})
        conn.close()
    except sqlite3.IntegrityError:
        print("Error get project tasks")

def get_tasks_for_member_test():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        employee_id = int(input("Input employee id:"))
        cursor = conn.execute('SELECT * FROM task WHERE task_id IN (SELECT task_id FROM employee_task WHERE employee_id=?);', (employee_id,))
        for row in cursor:
            print({'task_id': row[0], 'subtask_dependency_id': row[1], 'fulfill_requirement_id': row[2], 'task_name': row[3], 'finished': row[4], 'task_deadline': row[5], 'task_description': row[6]})
        conn.close()
    except sqlite3.IntegrityError:
        print("Error get tasks for member")
    
def get_project_readiness_test():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        i = 0
        j = 0
        project_id = int(input("Input project id:"))
        cursor1 = conn.execute('SELECT * FROM requirement WHERE project_id=? AND requirement_fulfilled=0;', (project_id,))
        for row in cursor1:
            i += 1
        cursor2 = conn.execute('SELECT * FROM requirement WHERE project_id=? AND requirement_fulfilled=1;', (project_id,))
        for row in cursor2:
            j += 1
        print("Project ID: " , project_id , " is " , (j/(j+i))*100.0 , " percent ready!")
        conn.close()
    except sqlite3.IntegrityError:
        print("Error get project readiness")

def get_request_for_project_manager_test():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        manager_id = int(input("Input manager id:"))
        cursor = conn.execute('SELECT * FROM member_request WHERE manager_id=?;', (manager_id,))
        for row in cursor:
            print({'manager_id': row[0], 'member_id': row[1], 'request': row[2], 'request_date': row[3], 'request_fulfilled': row[4]})
        conn.close()
    except sqlite3.IntegrityError:
        print("Error get requirement")

def update_requirement_fulfilled_test():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        requirement_id = int(input("Input requirement id:"))
        conn.execute('UPDATE requirement SET requirement_fulfilled=1 WHERE requirement_id=?;', (requirement_id,))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        print("Error insert requirement")

def get_all_requirements_test():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM requirement;')
        for row in cursor:
            print({'requirement_id': row[0], 'project_id': row[1], 'requirement_title': row[2], 'project_priority_level': row[3], 'core_feature': row[4], 'requirement_fulfilled': row[5], 'cost_to_fulfill': row[6]})
    except:
        print("Error")

    
################################################################################################################################################################################################################################################
##################################### GET STUFF FROM DATABASE (JSONIFIED) RELEASE EDITION ######################################################################################################################################################
################################################################################################################################################################################################################################################

# Returns straight lists of dictionaries to be returned to the functions to be JSON'd (JSON deez nuts lmao)

# With try excepts to prevent crashes also now returns a(n) (almost) blank dictionary if the query returns nothing
def get_project_members(project_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM get_employee_on_project WHERE project_id=?;', (project_id,))
        member_list = []
        for row in cursor:
            member_list.append({'employee_id': row[0], 'first_name': row[1], 'last_name': row[2], 'email': row[3], 'phone': row[4], 'project_role': row[5], 'project_id': row[6]})
        if (len(member_list) == 0):
            member_list.append({'employee_id': 0, 'first_name': " No employees yet ", 'last_name': "  ", 'email': " N/A ", 'phone': 9999999999999999, 'project_role': " N/A ", 'project_id': 0})
        return member_list
    except:
        return [{'employee_id': 0, 'email': " N/A ", 'first_name': " No employees yet ", 'last_name': "  ", 'phone': 9999999999999999, 'project_role': 'N/A', 'project_id': 0}]

def get_project_from_manager(manager_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM project WHERE manager_id=?;', (manager_id,))
        project_list = []
        for row in cursor:
            project_list.append({'project_id': row[0], 'manager_id': row[1], 'project_title': row[2], 'project_deadline': row[3], 'project_budget': row[4], 'client_name': row[5], 'project_type': row[6]})
        if (len(project_list) == 0):
            project_list.append({'project_id': 0, 'manager_id': 0, 'project_title': " project title not found ", 'project_deadline': "2000-01-01", 'project_budget': 0, 'client_name': " client name not found ", 'project_type': " project type not found "})
        return project_list
    except:
        return [{'project_id': 0, 'manager_id': 0, 'project_title': " project title not found ", 'project_deadline': "2000-01-01", 'project_budget': 0, 'client_name': " client name not found ", 'project_type': " project type not found "}]

def get_all_employees():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM employee')
        employee_list = []
        for row in cursor:
            employee_list.append({'employee_id': row[0], 'email': row[1], 'first_name': row[2], 'last_name': row[3], 'phone': row[4]})
        if (len(employee_list) == 0):
            employee_list.append({'employee_id': 0, 'email': " email not found ", 'first_name': " employee name not found ", 'last_name': " employee name not found ", 'phone': 9999999999999999})
        return employee_list
    except:
        return [{'employee_id': 0, 'email': " email not found ", 'first_name': " employee name not found ", 'last_name': " employee name not found ", 'phone': 9999999999999999}]

def get_project_budget(project_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT project_budget from project WHERE project_id=?;', (project_id,))
        if (cursor.rowcount == 0):
            return [{'project_budget': 0}]
        for row in cursor:
            return row[0]
    except:
        return [{'project_budget': 0}]
    
def get_project_name(project_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT project_title from project WHERE project_id=?;', (project_id,))
        if (cursor.rowcount == 0):
            return [{'project_title': " project title not found "}]
        return cursor.fetchone()[0]
    except:
        return [{'project_title': " project title not found "}]
    
def get_project_deadline(project_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT project_deadline from project WHERE project_id=?;', (project_id,))
        if (cursor.rowcount == 0):
            return [{'project_deadline': "2000-01-01"}]
        for row in cursor:
            return row[0]
    except:
        return [{'project_deadline': "2000-01-01"}]

def get_project_requirements(project_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM requirement WHERE project_id=?;', (project_id,))
        requirement_list = []
        for row in cursor:
            requirement_list.append({'requirement_id': row[0], 'project_id': row[1], 'requirement_title': row[2], 'project_priority_level': row[3], 'core_feature': row[4], 'requirement_fulfilled': row[5], 'cost_to_fulfill': row[6]})
        if (len(requirement_list) == 0):
            requirement_list.append({'requirement_id': 0, 'project_id': 0, 'requirement_title': " No requirements found ", 'project_priority_level': 0, 'core_feature': 0, 'requirement_fulfilled': 0, 'cost_to_fulfill': 0})
        return requirement_list
    except:
        return [{'requirement_id': 0, 'project_id': 0, 'requirement_title': " No requirements found ", 'project_priority_level': 'N/A', 'core_feature': 0, 'requirement_fulfilled': 0, 'cost_to_fulfill': 0}]

def get_project_tasks(project_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)        
        cursor = conn.execute('SELECT * FROM task WHERE fulfill_requirement_id IN (SELECT requirement_id FROM requirement WHERE project_id=?) ORDER BY task_deadline;', (project_id,))
        task_list = []
        for row in cursor:
            task_list.append({'task_id': row[0], 'subtask_dependency_id': row[1], 'fulfill_requirement_id': row[2], 'task_name': row[3], 'finished': row[4], 'task_deadline': row[5], 'task_description': row[6]})
        return task_list
    except:
        return [{'task_id': 0, 'subtask_dependency_id': 0, 'fulfill_requirement_id': 0, 'task_name': " task name not found ", 'finished': 0, 'task_deadline': " task deadline not found ", 'task_description': " task description not found "}]

def get_tasks_for_member(employee_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM task WHERE task_id IN (SELECT task_id FROM employee_task WHERE employee_id=?);', (employee_id,))
        task_list = []
        for row in cursor:
            task_list.append({'task_id': row[0], 'subtask_dependency_id': row[1], 'fulfill_requirement_id': row[2], 'task_name': row[3], 'finished': row[4], 'task_deadline': row[5], 'task_description': row[6]})
        if (len(task_list) == 0):
            task_list.append({'task_id': 0, 'subtask_dependency_id': 0, 'fulfill_requirement_id': 0, 'task_name': " task name not found ", 'finished': 0, 'task_deadline': " task deadline not found ", 'task_description': " task description not found "})
        return task_list
    except:
        return [{'task_id': 0, 'subtask_dependency_id': 0, 'fulfill_requirement_id': 0, 'task_name': " task name not found ", 'finished': 0, 'task_deadline': " task deadline not found ", 'task_description': " task description not found "}]

def get_project_readiness(project_id): # Returns a percentage of how ready the project is based on ratio of fulfilled requirements to total requirements
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        i = 0
        j = 0
        cursor1 = conn.execute('SELECT * FROM requirement WHERE project_id=? AND requirement_fulfilled=0;', (project_id,))
        for row in cursor1:
            i += 1
        cursor2 = conn.execute('SELECT * FROM requirement WHERE project_id=? AND requirement_fulfilled=1;', (project_id,))
        for row in cursor2:
            j += 1
        if (j+i == 0):
            return 100.0
        return (j/(j+i))*100.0
    except:
        return 0.0

def get_request_for_project_manager(manager_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM member_request WHERE manager_id=?;', (manager_id,))
        request_list = []
        for row in cursor:
            request_list.append({'request_id': row[0], 'manager_id': row[1], 'member_id': row[2], 'request': row[3], 'request_date': row[4], 'request_fulfilled': row[5]})
        if (len(request_list) == 0):
            request_list.append({'request_id': 0, 'manager_id': 0, 'member_id': 0, 'request': " request not found ", 'request_date': " request date not found ", 'request_fulfilled': 0})
        return request_list
    except:
        return [{'request_id': 0, 'manager_id': 0, 'member_id': 0, 'request': " request not found ", 'request_date': " request date not found ", 'request_fulfilled': 0}]

def get_request_for_employee(employee_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM member_request WHERE member_id=?;', (employee_id,))
        request_list = []
        for row in cursor:
            request_list.append({'request_id': row[0], 'manager_id': row[1], 'member_id': row[2], 'request': row[3], 'request_date': row[4], 'request_fulfilled': row[5]})
        if (len(request_list) == 0):
            request_list.append({'request_id': 0, 'manager_id': 0, 'member_id': 0, 'request': " request not found ", 'request_date': " request date not found ", 'request_fulfilled': 0})
        return request_list
    except:
        return [{'request_id': 0, 'manager_id': 0, 'member_id': 0, 'request': " request not found ", 'request_date': " request date not found ", 'request_fulfilled': 0}]

def get_skill_for_employee(employee_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM get_employee_skills WHERE employee_id=?;', (employee_id,))
        skill_list = []
        for row in cursor:
            skill_list.append({'employee_id': row[0], 'skill_id': row[1], 'skill_name': row[3]})
        if (len(skill_list) == 0):
            skill_list.append({'employee_id': 0, 'skill_id': 0, 'skill_name': " skill name not found "})
        return skill_list
    except:
        return [{'employee_id': 0, 'skill_id': 0}]

def get_main_skill_for_employee(employee_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM employee_skill WHERE employee_id=? AND skill_main=1;', (employee_id,))
        skill = cursor.fetchone()
        return skill
    except:
        return {'employee_id': 0, 'skill_id': 0, 'skill_main': 0}

def get_all_skills():
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM skill;')
        skill_list = []
        for row in cursor:
            skill_list.append({'skill_id': row[0],  'skill_name': row[1], 'skill_description': row[2]})
        if (len(skill_list) == 0):
            skill_list.append({'skill_id': 0, 'skill_name': " skill name not found ", 'skill_description': " skill description not found "})
        return skill_list
    except:
        return [{'skill_id': 0, 'skill_name': " skill name not found ", 'skill_description': " skill description not found "}]

def get_skill_for_requirement(requirement_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM join_requirement_skill WHERE requirement_id=?;', (requirement_id,))
        skill_list = []
        for row in cursor:
            skill_list.append({'requirement_title': row[2], 'skill_title': row[4], 'skill_description': row[5], 'skill_id': row[3]})
        if (len(skill_list) == 0):
            skill_list.append({'requirement_title': " requirement title not found ", 'skill_title': " skill title not found ", 'skill_description': " skill description not found ", 'skill_id': 0})
        return skill_list
    except:
        return [{'requirement_title': " requirement title not found ", 'skill_title': " skill title not found ", 'skill_description': " skill description not found ", 'skill_id': 0}]

def get_project_manager_details(manager_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM project_manager WHERE employee_id=?;', (manager_id,))
        manager_list = []
        for row in cursor:
            manager_list.append({'employee_id': row[0], 'email': row[1], 'first_name': row[2], 'last_name': row[3], 'phone_number': row[4], 'github_token' : row[5]})
        if (len(manager_list) == 0):
            manager_list.append({'employee_id': 0, 'email': " email not found ", 'first_name': " first name not found ", 'last_name': " last name not found ", 'phone_number': 999999999999999999})
        return manager_list
    except:
        return [{'employee_id': 0, 'email': " email not found ", 'first_name': " first name not found ", 'last_name': " last name not found ", 'phone_number': 999999999999999999}]

def get_employee_details(member_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM employee WHERE employee_id=?;', (member_id,))
        employee_list = []
        for row in cursor:
            employee_list.append({'employee_id': row[0], 'email': row[1], 'first_name': row[2], 'last_name': row[3], 'phone_number': row[4]})
        if (len(employee_list) == 0):
            employee_list.append({'employee_id': 0, 'email': " email not found ", 'first_name': " first name not found ", 'last_name': " last name not found ", 'phone_number': 999999999999999999})
        return employee_list
    except:
        return [{'employee_id': 0, 'email': " email not found ", 'first_name': " first name not found ", 'last_name': " last name not found ", 'phone_number': 999999999999999999}]

def get_percentage_task_completed(project_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        i = 0
        j = 0
        cursor1 = conn.execute('SELECT * FROM task WHERE fulfill_requirement_id IN (SELECT requirement_id FROM requirement WHERE project_id=?) AND finished=0;', (project_id,))
        for row in cursor1:
            i += 1
        cursor2 = conn.execute('SELECT * FROM task WHERE fulfill_requirement_id IN (SELECT requirement_id FROM requirement WHERE project_id=?) AND finished=1;', (project_id,))
        for row in cursor2:
            j += 1
        if (j+i == 0):
            return [0.0, 0.0, 100.0]
        return [(i+j) , (j),  (j/(j+i))*100.0]
    except:
        return 0.0

def get_all_employees_with_skill(skill_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM employee WHERE employee_id IN (SELECT employee_id FROM employee_skill WHERE skill_id=?);', (skill_id,))
        employee_list = []
        for row in cursor:
            employee_list.append({'employee_id': row[0], 'email': row[1], 'first_name': row[2], 'last_name': row[3], 'phone_number': row[4]})
        if (len(employee_list) == 0):
            employee_list.append({'employee_id': 0, 'email': " email not found ", 'first_name': " first name not found ", 'last_name': " last name not found ", 'phone_number': 999999999999999999})
        return employee_list
    except:
        return [{'employee_id': 0, 'email': " email not found ", 'first_name': " first name not found ", 'last_name': " last name not found ", 'phone_number': 999999999999999999}]

def get_skill_name_from_id(skill_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT skill_title FROM skill WHERE skill_id=?;', (skill_id,))
        skill_name = cursor.fetchone()[0] # if fetchone() returns None, then it will throw an error and will jump to the except block
        return skill_name
    except:
        return [{'skill_id': 0, 'skill_name': " skill name not found ", 'skill_description': " skill description not found "}]

def get_project_id_from_name(project_name):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT project_id FROM project WHERE project_title=?;', (project_name,))
        project_id = cursor.fetchone()[0]
        return project_id
    except:
        return 0

def get_project_from_id(project_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM project WHERE project_id=?;', (project_id,))
        project = cursor.fetchone()
        return project
    except:
        return [{'project_id': 0, 'project_title': " project title not found ", 'project_description': " project description not found ", 'project_budget': 0, 'project_readiness': 0, 'project_manager_id': 0}]
    
def check_if_user_exists(email, employee_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT * FROM employee WHERE email=? AND employee_id=?;', (email, employee_id))
        employee = cursor.fetchone()
        if (employee == None):
            return False
        return True
    except:
        return False
    
def get_employee_name(employee_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT first_name, last_name FROM employee WHERE employee_id=?;', (employee_id,))
        for row in cursor:
            return row[0] + ' ' + row[1]
    except:
        return "Error"

# get risk number and budgetary advice to be displayed on the dashboard
def get_estimates(project_id):
    try:
        conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
        cursor = conn.execute('SELECT project_risk, advice FROM estimates WHERE project_id=?;', (project_id,))
        row = cursor.fetchone()
        estimates = {
            'project_risk': row[0],
            'advice': ast.literal_eval(row[1])
        }
        return estimates
    except:
        return {'project_risk': None, 'advice': 'No advice available'}

def get_github_analysis():
    analysis_list = getGitHubAnalysis(current_project)
    return analysis_list


################################################################################################################################################################################################################################################
##################################### START OF MAIN PROGRAM ####################################################################################################################################################################################
################################################################################################################################################################################################################################################

if __name__ == '__main__':
    # Create a connection to the SQLite database
    app.run(debug=True, host='0.0.0.0')

###################################
#⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿#
#⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿#
#⣿⣿⣿⣿⣿⣿⣿⣿⡿⢋⣩⣭⣶⣶⣮⣭⡙⠿⣿⣿⣿⣿⣿⣿#
#⣿⣿⣿⣿⣿⣿⠿⣋⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡙⢿⣿⣿⣿#
#⣿⣿⣿⣿⣿⡃⠄⠹⡿⣿⣿⣿⣿⠟⠛⣿⣿⣿⣿⣷⡌⢿⣿⣿#
#⣿⣿⣿⣿⣿⠐⣠⡶⣶⣲⡎⢻⣿⣤⣴⣾⣿⣿⣿⣿⣿⠸⣿⣿#
#⣿⠟⣋⡥⡶⣞⡯⣟⣾⣺⢽⡧⣥⣭⣉⢻⣿⣿⣿⣿⣿⣆⢻⣿#
#⡃⣾⢯⢿⢽⣫⡯⣷⣳⢯⡯⠯⠷⠻⠞⣼⣿⣿⣿⣿⣿⣿⡌⣿#
#⣦⣍⡙⠫⠛⠕⣋⡓⠭⣡⢶⠗⣡⣶⡝⣿⣿⣿⣿⣿⣿⣿⣧⢹#
#⣿⣿⣿⣿⣿⣿⣘⣛⣋⣡⣵⣾⣿⣿⣿⢸⣿⣿⣿⣿⣿⣿⣿⢸#
#⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⣿⣿⣿⣿⣿⢸#
#⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⣿⣿⣿⣿⣿⣿⢸#
###################################

