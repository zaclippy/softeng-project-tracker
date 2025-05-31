/*
This is the schema file for our project database.
It contains all the tables and their attributes specified in the original design documents.
We can add more tables and attributes as we go along depending on the needs of the frontend and ML aspects.
*/

CREATE TABLE IF NOT EXISTS member_request(
  request_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT  DEFAULT(0),
  manager_id INTEGER NOT NULL,
  member_id INTEGER NOT NULL,
  request TEXT NOT NULL,
  request_date TIMESTAMP NOT NULL,
  request_fulfilled BOOLEAN,
  CONSTRAINT FK_member_request_manager FOREIGN KEY(manager_id)
    REFERENCES project_manager(employee_id)
  CONSTRAINT FK_member_request_member FOREIGN KEY(member_id)
    REFERENCES project_team_member(employee_id)
);

CREATE TABLE IF NOT EXISTS employee(
  employee_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT DEFAULT(0),
  email TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  phone_number INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS project_team_member(
  employee_id INTEGER NOT NULL PRIMARY KEY,
  project_id INTEGER DEFAULT(0),
  project_role TEXT DEFAULT 'UNASSIGNED',
  CONSTRAINT FK_employee FOREIGN KEY(employee_id)
    REFERENCES employee(employee_id),
  CONSTRAINT FK_member_project_team FOREIGN KEY(project_id)
    REFERENCES project(project_id)
);

CREATE TABLE IF NOT EXISTS project_manager(
  employee_id INTEGER NOT NULL PRIMARY KEY,
  email TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  phone_number INTEGER NOT NULL,
  github_token TEXT NOT NULL,
  CONSTRAINT FK_mannager_id FOREIGN KEY(employee_id)
    REFERENCES employee(employee_id)
);

CREATE TABLE IF NOT EXISTS task(
  task_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT DEFAULT(0),
  subtask_dependency_id INTEGER,
  fulfill_requirement_id INTEGER NOT NULL,
  task_name TEXT NOT NULL,
  finished BOOLEAN NOT NULL DEFAULT FALSE,
  task_deadline DATETIME NOT NULL,
  task_description TEXT NOT NULL,
  CONSTRAINT FK_task_requirement FOREIGN KEY(fulfill_requirement_id)
    REFERENCES requirement(requirement_id)
  CONSTRAINT FK_task_subtask FOREIGN KEY(subtask_dependency_id)
    REFERENCES task(task_id)
);

CREATE TABLE IF NOT EXISTS project(
  project_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT  DEFAULT(0),
  manager_id INTEGER NOT NULL,
  project_title TEXT NOT NULL UNIQUE,
  project_deadline DATETIME NOT NULL,
  project_budget INTEGER NOT NULL CHECK (project_budget >= 0),
  client_name TEXT NOT NULL,
  project_type TEXT NOT NULL,
  github_token TEXT NOT NULL,
  CONSTRAINT FK_project_project_manager FOREIGN KEY(manager_id)
    REFERENCES project_manager(employee_id)
);


CREATE TABLE IF NOT EXISTS requirement(
  requirement_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT  DEFAULT(0),
  project_id INTEGER NOT NULL,
  requirement_title VARCHAR(100) NOT NULL,
  project_priority_level TEXT NOT NULL DEFAULT('MEDIUM'),
  core_feature BOOLEAN NOT NULL DEFAULT FALSE,
  requirement_fulfilled BOOLEAN NOT NULL DEFAULT FALSE,
  cost_to_fulfill FLOAT NOT NULL CHECK (cost_to_fulfill >= 0),

  CONSTRAINT FK_requirement_project FOREIGN KEY(project_id)
    REFERENCES project(project_id)
);

CREATE TABLE IF NOT EXISTS employee_task(
  employee_id INTEGER NOT NULL,
  task_id INTEGER NOT NULL,
  employee_finished BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (employee_id,task_id),
  CONSTRAINT FK_employee_task_employee FOREIGN KEY(employee_id)
    REFERENCES project_team_member(employee_id),
  CONSTRAINT FK_employee_task_task FOREIGN KEY(task_id)
    REFERENCES task(task_id)
);

CREATE TABLE IF NOT EXISTS employee_skill(
  employee_id INTEGER NOT NULL,
  skill_id INTEGER NOT NULL,
  skill_main BOOLEAN NOT NULL DEFAULT 0,
  PRIMARY KEY(employee_id,skill_id),
  CONSTRAINT FK_employee_skill_employee FOREIGN KEY(employee_id)
    REFERENCES project_team_member(employee_id),
  CONSTRAINT FK_employee_skill_skill FOREIGN KEY(skill_id)
    REFERENCES skill(skill_id)
);

CREATE TABLE IF NOT EXISTS skill(
  skill_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT  DEFAULT(0),
  skill_title TEXT NOT NULL,
  skill_description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS skill_requirement(
  skill_id INTEGER NOT NULL,
  requirement_id INTEGER NOT NULL,
  PRIMARY KEY(skill_id,requirement_id),
  CONSTRAINT FK_skill_requirement_skill FOREIGN KEY(skill_id)
    REFERENCES skill(skill_id),
  CONSTRAINT FK_skill_requirement_requirement FOREIGN KEY(requirement_id)
    REFERENCES requirement(requirement_id)
);

CREATE TABLE IF NOT EXISTS estimates(
  project_id INTEGER NOT NULL PRIMARY KEY,
  thousand_lines_of_code INTEGER DEFAULT(0),
  completion_months_est INTEGER DEFAULT(0),
  spent_money_est INTEGER DEFAULT(0),
  project_risk INTEGER DEFAULT(0),
  advice TEXT,
  CONSTRAINT FK_estimates_project FOREIGN KEY(project_id)
    REFERENCES project(project_id)
);
  
CREATE VIEW get_employee_on_project AS 
SELECT employee.employee_id, employee.first_name, employee.last_name, employee.email, employee.phone_number, project_team_member.project_role, project_team_member.project_id
  FROM employee
  INNER JOIN project_team_member ON employee.employee_id = project_team_member.employee_id
  GROUP BY employee.employee_id, employee.first_name, employee.last_name, employee.email, employee.phone_number, project_team_member.project_role, project_team_member.project_id;

CREATE VIEW get_employee_skills AS 
SELECT employee_skill.employee_id, employee_skill.skill_id, employee_skill.skill_main, skill.skill_title, skill.skill_description
  FROM employee_skill
  INNER JOIN skill ON employee_skill.skill_id = skill.skill_id
  GROUP BY employee_skill.employee_id, employee_skill.skill_id, employee_skill.skill_main, skill.skill_title, skill.skill_description;

CREATE VIEW join_requirement_skill AS
SELECT requirement.requirement_id, requirement.project_id, requirement.requirement_title, skill.skill_id, skill.skill_title, skill.skill_description
  FROM skill_requirement
  INNER JOIN requirement ON skill_requirement.requirement_id             = requirement.requirement_id
  INNER JOIN skill       ON skill_requirement.skill_id                   = skill.skill_id
  GROUP BY requirement.requirement_id, requirement.project_id, requirement.requirement_title, skill.skill_id, skill.skill_title, skill.skill_description;

