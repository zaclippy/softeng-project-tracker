# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 15:43:01 2023
@author: Adam
"""

from github import Github
import datetime
import sqlite3
import numpy

def getGitHubAnalysis(projectID):
    # row=0
    # Connect to the database
    conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
    
    # Get token from the database
    cursor = conn.execute('SELECT github_token from project WHERE project_id=?;', (projectID,))
    for row in cursor:
        token = str(row[0])
    
    if len(row) == 0:
        exit()
    
    # Token to be read from database in final version
    gh = Github(token)
    
    # Get project deadline from the database
    cursor = conn.execute('SELECT project_deadline from project WHERE project_id=?;', (projectID,))
    for row in cursor:
        deadline = row[0]
    
    # Get project employee count from the database
    cursor = conn.execute('SELECT COUNT(*) FROM get_employee_on_project WHERE project_id=?;', (projectID,))
    for row in cursor:
        employeeCount = row[0]
    
    # Get project name from the database
    cursor = conn.execute('SELECT project_title FROM project WHERE project_id=?;', (projectID,))
    for row in cursor:
        projectName = row[0]
        
    # Get line estimate from the database
    cursor = conn.execute('SELECT thousand_lines_of_code FROM estimates WHERE project_id=?;', (projectID,))
    for row in cursor:
        estimatedLOC = int(row[0]) * 1000
        
    if len(row) == 0:
        exit()
    
    # Include username if no token
    account = gh.get_user() 
    
    # Get repository based on inputted name
    rep = account.get_repo(str(projectName.replace(" ", "-")))
    
    totalLines = 0
    totalEmpty = 0
    totalCommentDensity = 0
    totalFiles = 0
    currentTime = datetime.datetime.now()
    
    # Examine all contents of the repository
    repContents = rep.get_contents("") 
    commits = rep.get_commits()
    #Total number of commits
    countCommits = commits.totalCount 
    
    # Get unique hash for the most recent commit
    latestSha = commits[0].sha
    latestCommit = rep.get_commit(latestSha)
    # Get the time at which that commit was made
    newTime = latestCommit.commit.author.date
        
    # Get unique hash for the oldest commit
    oldestSha = commits[countCommits-1].sha
    oldestCommit = rep.get_commit(oldestSha)
    # Get the time at which that commit was made
    oldTime = oldestCommit.commit.author.date
     
    # Calculate how long this repository has been worked on (since first commit, not creation of the repository, as that is when development begins)
    devYears = newTime.year - oldTime.year
    devMonths = newTime.month - oldTime.month
    devDays = newTime.day - oldTime.day
    devHours = newTime.hour - oldTime.hour
    months = devYears/12 + devMonths + (devDays + (devHours/24))/30
    
    # Use this time to calculate average number of commits per month
    if months != 0:
        commitsPerMonth = int(countCommits/months)
    else:
        commitsPerMonth = 0
    
    contributorCount = rep.get_contributors().totalCount
    #contributorCount = 5

    severeFixTime = 0
    poorFixTime = 0
    totalFixTime = 0
    averageFixTime = 0 # referenced before assignment errors
    
    issuesOpen = rep.get_issues(state='open')
    issuesOLengths = []
    for issue in issuesOpen:
        createdAt = issue._created_at.value
        openFor = currentTime - createdAt
        daysOpen = openFor.days
        issuesOLengths.append(daysOpen)
        
        severeFixTime = 0
        poorFixTime = 0
        totalFixTime = 0
        averageFixTime = 0
        
    if len(issuesOLengths) != 0:
        for each in issuesOLengths:
            if each > (months*30)/2:
                severeFixTime += 1
            elif each > (months*30)/5:
                poorFixTime += 1
        
    issuesClosed = rep.get_issues(state='closed')
    issuesCLengths = []
    for issue in issuesClosed:
        createdAt = issue._created_at.value
        closedAt = issue._closed_at.value
        openFor = closedAt - createdAt
        timeOpen = openFor.days + openFor.seconds/86400
        issuesCLengths.append(timeOpen)
        
    if len(issuesCLengths) != 0:
        for each in issuesCLengths:
            totalFixTime += each
                
        averageFixTime = round(totalFixTime / len(issuesCLengths), 2)
        
    # For each file/folder in the repository:
    for content in repContents:
        # Title of file/folder 
        name = content.name
        # Try to find the first instance of a '.', to determine a file's filetype
        try:
            place = name.index(".")
            fileType = name[place:]
        # If an error occurs (due to having no '.' in the title, assign an obvious non-value)
        except:
            fileType = 0
    
        # If the piece of content in question is a folder:
        if content.type == "dir":
            # Extend the path inside the folder, to reach any files or sub-folders which are inside
            repContents.extend(rep.get_contents(content.path))
        # If the piece of content in question is a file:
        else:
            totalFiles += 1
            # Multiline string containing file's content
            cleaned = content.decoded_content.decode()
            empty = cleaned.count("\n\n")
            # Calculate total length of the file
            linesInFile = len(cleaned.splitlines())-empty 
            
            #Keep a total of lines in this repository (project)
            totalLines += linesInFile
            totalEmpty += empty
            # Count the number of comments in the code (syntax depending on filetype)
            comments = 0
            if fileType == ".py":
                comments = cleaned.count("#") + (cleaned.count("'''"))/2 + (cleaned.count("\"\"\""))/2
            elif fileType == ".c" or fileType == ".java" or fileType == ".js":
                comments = cleaned.count("/*") + cleaned.count("//")
            elif fileType == ".html":
                comments = cleaned.count("<!--")
                
            if linesInFile > 0:
                # Calculate the proportion of the whole file which are comments (0 is none, 1 is the entire file being only comments)
                commentDensity = round(comments/linesInFile,2)
            else:
                commentDensity = 0
            # Keep track of the total comment density, so the overall average can be found
            totalCommentDensity += commentDensity
    
    if totalFiles == 0 or totalLines + totalEmpty == 0:
        return ["There is no code in this repository!"]
        
    emptyLineDensity = round(totalEmpty/(totalLines + totalEmpty), 2)
    # Calculate the overall average comment density for the repository (project)
    overallCommentDensity = totalCommentDensity/totalFiles
    
    # Calculate the average amount of lines which are written per month 
    if months != 0:
        linesPerMonth = int(totalLines / months)
    else:
        linesPerMonth = 0
        
    # Convert the deadline from the database into datetime format 
    deadline = datetime.date(int(deadline[0:4]), int(deadline[5:7]), int(deadline[8:10]))
    
    # Calculate how many months are left until the deadline (Assuming 1 month = 30 days, is rounded to whole number so not a big deal)
    remainingMonths = int((deadline.year - currentTime.year)*12 + (deadline.month - currentTime.month) + (deadline.day - currentTime.day)/30)
    # Should be taken from database, calculated in initial estimation
    #estimatedLOC = 10000 
     
    # Calculate a value to represent how on-track the project is in terms of lines of code. 1 means the code will be finished exactly on time, lower means it won't be done in time, higher means it will be done before the deadline
    LOCTrackValue = round(1 - (estimatedLOC-(linesPerMonth*remainingMonths))/estimatedLOC, 1)
    
    #Calculate the proportion of the team which contribute
    if employeeCount == 0:
        teamContribution = 0
    else:
        teamContribution = contributorCount/employeeCount
    
    #List which will be filled with strings for advice
    outputList = []
    acceptable = 0
    
    title = "Progress Rate"
    if LOCTrackValue == 0:
        result = "No Progress"
        comment = "There has been no progress in the code. Begin coding as soon as possible."
    elif LOCTrackValue < 1:
        result  = str(int(((1-LOCTrackValue)/LOCTrackValue)*100)) + "%"
        comment = "slower than is needed to finish the code in time. Speak to developers about increasing their productivity."
    elif LOCTrackValue < 1.5:
        result = "On Track"
        comment = "The project is progressing at a good pace."
        acceptable += 1
    else:
        result = str(int(((LOCTrackValue-1.5)/LOCTrackValue)*100)) + "%"
        comment = "faster than is reasonable. Check that code isn't being rushed."
    
    outputList.append([title, result, comment])
    
    title = "Comments"
    
    if employeeCount < 5:
        if overallCommentDensity == 0:
            result = "0"
            comment = "There are no comments in the code. It is important to add comments to code so it can be better understood by other developers."
        elif overallCommentDensity < 0.1:
            result = str(int((0.1-overallCommentDensity)/overallCommentDensity*100)) + "%"
            comment = "lower than is ideal. Even with a small team, it is important to comment code as it is written to avoid confusion."
        elif overallCommentDensity < 0.4:
            result = "Good"
            comment = ("There is a good amount of comments in the code.")
            acceptable += 1
        else:
            result = str(int(((overallCommentDensity-0.4)/overallCommentDensity)*100)) + "%"
            comment = "more than should be necessary. They should by descriptive, but not overwhelming."
    else:
        if overallCommentDensity == 0:
            result = "0"
            comment = "There are no comments in the code. It is important to add comments to code so it can be better understood by other developers."
        elif overallCommentDensity < 0.2:
            result = str(int((0.2-overallCommentDensity)/overallCommentDensity*100)) + "%"
            comment = "lower than is ideal. With a larger team, it is important to add comments so everyone understands code written by others."
        elif overallCommentDensity < 0.5:
            result = "Good"
            comment = ("There is a good amount of comments in the code.")
            acceptable += 1
        else:
            result = str(int(((overallCommentDensity-0.5)/overallCommentDensity)*100)) + "%"
            comment = "more than should be necessary. They should by descriptive, but not overwhelming."
    
    outputList.append([title, result, comment])
    
    title = "Code Spacing"
    if emptyLineDensity == 0:
        result = "0"
        comment = "There are no empty lines in the code. It is important to add empty lines to code so it can be read easier."
    elif emptyLineDensity < 0.15:
        result = str(int(((0.15-emptyLineDensity)/emptyLineDensity)*100)) + "%"
        comment = "lower than is ideal. The code would benefit from having more empty lines between different sections of code - this helps to differentiate tasks, and aid readability."
    else:
        result = "Good"
        comment = "The code is spaced well and readable."
        acceptable += 1
    
    outputList.append([title, result, comment])
    
    title = "Unacceptably Slow Issue Resolutions"
    
    if severeFixTime > 0:
        result = str(severeFixTime)
        comment = "issues which have been left unresolved for over half of the development time. It can be much more effort-intensive to fix issues once the code is almost finished, than if it were fixed earlier."
    else:
        result = "None"
        comment = "No issues were left for a severely long time."
        acceptable += 1
        
    outputList.append([title, result, comment])
    
    title = "Slow Issue Resolutions"
    
    if poorFixTime > 0:
        result = str(poorFixTime)
        comment = "issues which have been left unresolved for over a fifth of the development time. It is important to fix issues early, otherwise other sections of code using related content may also need changing."
    else:
        result = "None"
        comment = "No issues were left for a long time."
        acceptable += 1
        
    outputList.append([title, result, comment])
    
    if (months == 0):
        proportionalFixTime = 0
    else: 
        proportionalFixTime = averageFixTime/(months*30)
    
    title = "Issue Fix Time"
    
    if proportionalFixTime > 0.2:
        result = str(int(((proportionalFixTime-0.2)/proportionalFixTime)*100)) + "%"
        comment = "lower than is ideal. Issues must be adressed quickly, in order for progress to continue smoothly."
    elif proportionalFixTime > 0.1:
        result = "Acceptable"
        comment = "The resolution time for issues is acceptable."
        acceptable += 1
    else:
        result = "Good"
        comment = "The resolution time for issues is good."
        acceptable += 1
    
    outputList.append([title, result, comment])
    
    title = "Team Contribution"
    
    if teamContribution < 0.8:
        result = str(int(numpy.ceil((employeeCount - contributorCount)*0.8)))
        comment = "fewer team members are contributing than there should be. It is important that the workload is split evenly amongst the team."
    else:
        result = "Good"
        comment = "Team contribution is at a good level."
        acceptable += 1
    
    outputList.append([title, result, comment])
    commitsPerPersonPerMonth = commitsPerMonth/contributorCount
    
    title = "Commit Frequency"
    if commitsPerPersonPerMonth == 0:
        result = 0
        comment = "There have been no commits in the last month. It is important to regularly commit code in order to keep the project progressing."
    elif commitsPerPersonPerMonth < 15:
        result = str(int((15-commitsPerPersonPerMonth)/commitsPerPersonPerMonth*100)) + "%"
        comment = "lower frequency than is ideal. Frequent updates allows for the whole team to be on the same page when working on the project."
    else:
        result = "Good"
        comment = "The code repository is being updated frequently enough."
        acceptable += 1
        
    outputList.append([title, result, comment])
    outputList.append((int(acceptable/8*100)))
    
    return outputList

