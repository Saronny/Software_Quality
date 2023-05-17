
**Analysis 3: Object-Oriented Modelling (INFANL03-3 | INFANL23-3)	OP3 | 2020-2021	CMI | HR**

<a name="_rm6enrzhy38q"></a>**Final Assignment**

|<a name="_rfskqarasyi2"></a>**ANALYSIS 8: SOFTWARE QUALITY (INFSWQ01-A | INFSWQ21-A)**|
| :- |

<a name="_7bpk6aibre3q"></a>**Educational Period 4 [2022-23]**

-----

To make it feasible as an assessment for this course, the following scenario is formulated to ensure that students have achieved at least the minimum level of the course learning outcomes, as defined in the course manual. Please note that this scenario might be very different in real world cases, which usually need other quality requirements. Normally such a system would involve many other requirements and components, but here you can limit yourself only to the given description.


|<h1><a name="_21wbcmgumepj"></a>**Learning Objectives**</h1>|
| :- |
## -----
<a name="_gxcv4ra4szkr"></a>The learning objectives of the assignment and mapping to the intended learning outcome of the course are listed below:

1. To understand the common mistakes of coders in input validation and communications with subsystems (LO2, LO3).
1. To apply the knowledge of input validation, SQL injection, and cryptography (LO1, LO4).
1. To partially build a secure system against various attacks initiated by user input (LO4).


|<h1><a name="_dnxbp8pjtulf"></a>**Assignment**</h1>|
| :- |
## -----
## <a name="_xzs1nkkh7vvf"></a><a name="_rj3g26fwz60i"></a>**Introduction**
In this assignment, we would like to make a simple system to store and manage the information of members of Fitness Plus (Fit+), a health and fitness club where various services are offered to help its members meet their fitness goals. It currently has over 53,000 members in the Netherlands. As a member in Fit+, in addition to the main workout area, which primarily consists of free weights including dumbbells and barbells and the stands and benches used with these items and exercise machines, which use gears, cables and other mechanisms to guide the user's exercise, you can also enjoy many extra benefits, such as cardio area, group exercise classes, snack/protein bars and smoothies, restaurants, child-care facilities, member lounges and cafes, and occasional discounts on health-shops selling equipment. To enjoy all these exciting member benefits, you must be a member of the club. They can be registered for free at a members’ service desk. A membership management system is needed at the customer service to register new members.

This assignment consists of the design and implementation of a simple console-based interface in Python 3 for the mentioned system. The system should use a local database to store the information of members. You should use SQLite 3 database for this purpose. Figure 1 in the next page, depicts a general overview and the components of the systems. 

Users are the employees of the company, which are categorized as below:

1. **Super Administrator** (Hardcoded) – A super admin has full control of the system.
1. **System Administrators** (to be defined by the Super Administrator only) – An admin who can manage trainers accounts (register new trainer, modify or delete a trainer, etc.)
1. **Trainers** (to be defined by a system administrator or a super administrator) – A trainer can manage members in the system (register new members, modify, search or retrieve their information.)

**Note that the members of the club are not users of the system (more details about the users and their roles can be found in following pages).**

When new member of the club request for membership, their information should be registered in the system, first. A new member can be registered in the system by a trainer (or a higher-level user, i.e., system admin or super admin). For a member, the following data must be entered to the system:

- First Name and Last Name
- Age, Gender, Weight
- Address (Street name, House number, Zip Code (DDDDXX), City (system should generate a list of 10 city names of your choice predefined in the system)
- Email Address
- Mobile Phone (+31-6-DDDDDDDD) – only DDDDDDDD to be entered by the user.

![](Aspose.Words.513775dc-3412-4350-9395-15d664e2a76f.003.png)The system then needs to automatically add the registration date and assign a unique membership ID to every new member. The membership ID is a string of 10 digits, formatted as below. The last digit on the right is a checksum digit, which must be equal to the remainder of the sum of the first 9 digits by 10. 

![](Aspose.Words.513775dc-3412-4350-9395-15d664e2a76f.004.png)

|ID|D|D|D|D|D|D|D|D|D|C|
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
|index|0|1|2|3|4|5|6|7|8|![](Aspose.Words.513775dc-3412-4350-9395-15d664e2a76f.005.png)9|

Registration year in shortened form.

For example, **23** for 20**23**.

Checksum
![](Aspose.Words.513775dc-3412-4350-9395-15d664e2a76f.006.png)![](Aspose.Words.513775dc-3412-4350-9395-15d664e2a76f.007.png)![](Aspose.Words.513775dc-3412-4350-9395-15d664e2a76f.008.png)

Randomly generated Any digit from 0 to 9

![](Aspose.Words.513775dc-3412-4350-9395-15d664e2a76f.009.png)


Few examples:

- Invalid ID number: **25**2328744**0** [we are still in year 2023, so the first 2 digits cannot be 25 yet]
- Invalid ID number: **22**2328742**4** [registered in 2022, but the checksum is incorrect]

(2+2+2+3+2+8+7+4+2) = 35 	35 mod 10 = 5 ¹ **4** 

- Valid ID number: 212328742**1**


**FINAL ASSIGNMENT: Furnicor Family System	PAGE 2**

**Analysis 3: Object-Oriented Modelling (INFANL03-3 | INFANL23-3)		OP3 | 2020-2021						CMI | HR**



Members’ information
Members
Trainers

Figure 1. Overview of the System 

`												`**PAGE 11**

**Analysis 3: Object-Oriented Modelling (INFANL03-3 | INFANL23-3)	OP3 | 2020-2021	CMI | HR**
## <a name="_zg2d7eb6p4k3"></a>**User Interface**
The minimum requirement for the user interface is a console-based interface with the possibility of menus or options to be chosen by user.

The system must have a user-friendly (easy, efficient, and enjoyable) interface to allow the users (super-admin, system-admins, or trainers) to perform their functions, easily and smoothly. 

Ensure that your user interface provides sufficient information for the user to work with it. For example, if you have a menu “1. Register new member” which should be chosen by pressing **‘R’** or **‘r’** or entering **1**, this should be clearly displayed to the user on the menus screen. Do not suppose that the user (and your teacher when testing and grading your assignment) should guess how to work with the user interface.

Note that the user interface would not be graded for flexibility or efficiency of use, but if your teachers cannot properly work with the system, it might not be possible for them to correctly assess your work.
## <a name="_azvs6maluuuh"></a>**Data (DB) File**
The main functionality of the system is to store and manage the information of the members in the system. In addition, the system needs to store information of the users of the system.

For this purpose, you need to implement the database using SQLite library in Python “sqlite3”. 

Note that the sensitive data, including usernames, and members’ data must be encrypted in the database. You must not store any password in the database, rather as you learned (or will learn soon) in the lessons, **you must only store the hash of password in the database**.
## <a name="_6rxwndtpw6z7"></a>**Stakeholders, Users, Authorization, Functions and Accessibility Levels**
More details about the stakeholders of the system are explained below:

1. **Members**

**Members are not the users of the system** and have no role or interaction with the application. The only relationship between members and the system is that their information is recorded and stored in the system by a company trainer (System admin and super admin should be also able to manage members’ data in the database).

1. **Trainers**

Trainers are employees of the club who are in direct contact with the members. They process the requests of the members. Hence, they need to be able to manage the member’s information and data. For this purpose, when a new client requests for membership, a trainer needs to register the client's information in the system. So, the minimum required functions of a trainer in the system are summarized as below:

- To update their own password
- To add a new member to the system
- To modify or update the information of a member in the system
- To search and retrieve the information of a member (check note 2 below).
1. **System Administrators**

A system administrator is a person who can maintain the system and perform some administration tasks on the application. They are IT technical people and not intended to work with the members. However, for security reasons, they should be able to perform all the functions of trainers, if needed. The minimum required functions of an administrator are listed below:

- To update their own password.
- To check the list of users and their roles.
- To define and add a new trainer to the system.
- To modify or update an existing trainer’s account and profile.
- To delete an existing trainer’s account.
- To reset an existing trainer’s password (a temporary password).
- To make a backup of the system and restore a backup (members information and users’ data).
- To see the logs file(s) of the system.
- To add a new member to the system.
- To modify or update the information of a member in the system.
- To delete a member's record from the database (note that a trainer cannot delete a record but can only modify or update a member’s information).
- To search and retrieve the information of a member.
1. **Super Administrator** 

Super administrator is simply the owner or the manager of the club. The manager needs a super admin password through which can define a system administrator. Although the main function of the super admin is to define system admin(s), and leave the system to them; however, they **should be able to perform all possible functionalities of the lower-level users** (i.e., system admin and trainer). 

In this assignment, to make it easier for your teacher to test and assess your work, a super admin must be hard coded with **username:** **super\_admin**, **password: Admin\_123!** 

- Note that we know this is not a good development practice in terms of the quality and security of the system, but this is only to enable your teacher to easily test your system using this predefined hardcoded username and password.

The minimum required functions of a super administrator are listed below:

- To check the list of users and their roles.
- To define and add a new trainer to the system.
- To modify or update an existing trainer’s account and profile.
- To delete an existing trainer’s account.
- To reset an existing trainer’s password (a temporary password).
- To define and add a new admin to the system.
- To modify or update an existing admin’s account and profile.
- To delete an existing admin’s account.
- To reset an existing admin’s password (a temporary password).
- To make a backup of the system and restore a backup (members information and users’ data).
- To see the logs file of the system.
- To add a new member to the system.
- To modify or update the information of a member in the system.
- To delete a member's record from the database (note that a trainer cannot delete a record, but can only modify or update a member’s information).
- To search and retrieve the information of a member.

**Note 1:** Trainers and system admins should have profiles, in addition to their usernames and passwords. Their profiles contain only first name, last name, and registration date.

**Note 2:** The search function must accept any data field as a search key (member ID, first name, last name, address, email address, and phone number). It must also accept partial keys. For example, a user can search for a member with a name “Mike Thomson” and member ID “2123287421” by entering any of these keys: “mik”, “omso”, or “2328”, etc.
## <a name="_r5vzbdwxkg0s"></a>**Log** 
The system should log all activities. All suspicious activities must be flagged, and the system needs to produce an alert/notification for unread suspicious activities, once a system administrator or super administrator is logged in to the system. Log file(s) must be encrypted and should be only readable through the system interface, by system administrator or super admin. It means that it should not be readable by any other tool, such as file explorer, browser, or text editor.

A log should be structured similar to the following sample:

|No.|Date|Time|Username|Description of activity|Additional Information|Suspicious|
| :- | :- | :- | :- | :- | :- | :- |
|1|12-05-2021|15:51:19|john\_m\_05|Logged in||No|
|2|12-05-2021|18:00:20|superadmin|New admin user is created|username: mike12|No|
|3|12-05-2021|18:05:33|…|Unsuccessful login|username: “mike12” is used for a login attempt with a wrong password|No|
|4|12-05-2021|18:07:10|…|Unsuccessful login|Multiple usernames and passwords are tried in a row|Yes|
|5|12-05-2021|18:08:02|superadmin|User is deleted|User “mike12” is deleted|No|
|...|...|...|...|...|...|...|

<a name="_qyspi3ubwuq"></a>Note that the table above is just a sample. You may choose your own desired format, but the information given above are the minimum information needed in the log file.
## **Encryption of sensitive data**
As mentioned before, all sensitive data in the database, including usernames, and members phones and addresses, as well as log data must be encrypted. For this encryption, you must use an asymmetric algorithm. 

**Additional Clarification:** At any point in time, whether the application is running or not running, any user with any text editor (outside of the Fit+ application) must not be able to see any meaningful data in the database or log file [unless they can decrypt the file(s)]. So, encryption and decryption of the files on start and exit is not an acceptable solution.
## **Passwords**
Note that any form of password (encrypted or unencrypted) is not allowed to be to be stored in the database or any other data file in the system. Instead, you must only store hash of passwords in the system. For this purpose, you are allowed to use a third-party library.
## <a name="_vszj2xa2ugz9"></a>**Backup**
The system administrator and super administrator should be able to create a backup of the system and restore the system from a backup. This backup must include the database (users and members information) and the log file(s) and should be in **zip** format. Note that the log files and sensitive data in the DB file must be already encrypted, and no additional encryption is needed when you are creating the backup zip file. The system must support multiple backups.
##
##

## <a name="_c85thv5lxsfg"></a>**Usernames and Passwords**
All Usernames and Passwords (except for the super admin which is hardcoded) must follow the rules given below:

- **Username**:
  - must be unique and have a length of at least 8 characters
  - must be no longer than 12 characters
  - must be started with a letter or underscores (\_)
  - can contain letters (a-z), numbers (0-9), underscores (\_), apostrophes ('), and periods (.)
  - no distinguish between lowercase or uppercase letters


- **Password**:
  - must have a length of at least 12 characters
  - must be no longer than 30 characters
  - can contain letters (a-z), (A-Z), numbers (0-9), Special characters such as ~!@#$%&\_-+=`|\(){}[]:;'<>,.?/
  - must have a combination of at least one lowercase letter, one uppercase letter, one digit, and one special character



<a name="_r6qi5xbarl6l"></a><a name="_3rigvzihfjbc"></a>**

|<h1>**Grading**</h1>|
| :- |
\-----

<a name="_bw4272cbaayh"></a>The assignment will be evaluated as either PASS or FAIL. To successfully pass the course, students must pass the assignment together with passing the exam.

Your assignment might be graded by your teacher (the teacher in your course time table) or another teacher (Babak, Ahmad, or Reza).

Students will receive feedback from the teachers during the presentation. We suggest you note all the comments, in case you cannot successfully pass the assignment, you can use the comments and feedback to apply in the next chance.

Your assignment will be assessed according to the following marking Scheme. To successfully pass the assignment you need to meet the following assessment criteria:

- **You must get C1 and C2 at least as Satisfactory (L2 or L3)**, and
- **You must get C3 and C6 at least as Satisfactory (L1)**, and
- **You must get C4 and C5 at least as L1**, and
- **You must get a minimum of 10 points in total**.

## <a name="_ysizfn4lzodp"></a><a name="_grading_table"></a>**Grading Table**

|Does the functionality of the submitted code match the assignment description?|Result |
| :- | :-: |
|<p>Functionality of the system as described.</p><p>- If unsatisfactory, the assignment is FAIL and could not be evaluated for grading.</p><p>- If satisfactory, then the table below will be used for grading.</p>|(Unsatisfactory/Satisfactory) |


|<a name="_cszd6aeemuu9"></a>**Criteria and Points**|**Unsatisfactory**|**Satisfactory**|
| :- | :-: | :-: |
|C1|Authentication and Authorization for users are properly implemented (Users access level)|L0|L1|L2|L3|
|C2|All inputs are properly validated.|L0|L1|L2|L3|
|C3|The system is secured against SQL injection.|L0|L1|
|C4|Invalid inputs are properly handled.|L0|L1|L2|L3|
|C5|All activities are properly logged and backed up.|L0|L1|L2|L3|
|C6|Students can properly demonstrate and explain the system.|L0|L1|
|<p>**C1, C2, C4, and C5:**</p><p>- **L0:** Not implemented / very basic attempts **[0 point]**</p><p>- **L1:** Poor implementation / Major problems **[1 point]**</p><p>- **L2:** Minimum requirements are implemented / Minor problems **[2 points]**</p><p>- **L3:** Meet the requirements / Good implementation **[3 points]**</p><p>**C3**:</p><p>- **L0:** Not implemented / Poor implementation / Major problems **[0 point]**</p><p>- **L1:** Minimum requirements are implemented / Minor problems **[1 point]**</p><p>**C6**:</p><p>- **L0:** presentation is not satisfactory **[0 point]**</p><p>- **L1:** presentation is satisfactory **[1 point]**</p>|

## <a name="_wue9v1baxum4"></a><a name="_marking_scheme"></a>**Marking Scheme**
An example of criteria and marking scheme is given in the table below. Please note that not all criteria are written in this table, but you can find all requirement and criteria in the assignment description which are already explained in detail. This table is to give you an idea of how the assessment procedure is. 


<table><tr><th colspan="1" rowspan="2">Criteria</td><th colspan="2">Unsatisfactory</td><th colspan="2">Satisfactory</td></tr>
<tr></td><td colspan="1">L0 (0 point)</td><td colspan="1">L1 (1 point)</td><td colspan="1">L2 (2 point)</td><td colspan="1">L3 (3 points)</td></tr>
<tr><td colspan="1">C1</td><td colspan="1"><p>Authenticating does not exist, or it is not working properly.</p><p>Authorization is not implemented or at a very basic level.</p></td><td colspan="1"><p>Authentication is based on username and passwords. Usernames and PWs do not conform the given format and are not hashed. Application code has hard-coded role checks.</p><p>Lack of centralized access control logic. There are some bugs or major problems.</p></td><td colspan="1">Authentication has proper error messages. Authentication data are stored in an encrypted file using proper mechanism. Passwords are hashed. Authorization is implemented based on user roles and is centralized. No bugs or major problems.</td><td colspan="1"><p>Authentication has a secure recovery mechanism. It is protected against multiple wrong tries.</p><p>Authorization is fully implemented based on the user's actions, without bugs or major problems.</p></td></tr>
<tr><td colspan="1">C2</td><td colspan="1">Input Validation is not implemented or at a very trivial level. There are many bugs or errors, which let Input Validation be bypassed easily.</td><td colspan="1">Input Validation is implemented, but not for all input types, or contains few bugs and errors. Input Validation can be still bypassed. Blacklisting or mixed mechanism is used.</td><td colspan="1">Input Validation is complete for all input types and does not allow bypassing. Whitelisting is used for all inputs without any flaw. There is no bug or error.</td><td colspan="1">Input Validation is fully implemented and there are signs of following good practices in validation, such as checking for NULL-Byte, range and length, Validation Functions, etc.</td></tr>
<tr><td colspan="1">C4</td><td colspan="1">Invalid inputs are not handled, or at very basic level, with many bugs or errors.</td><td colspan="1">There are some attempts of invalid input handling, but not correctly implemented. The reactions to different types of inputs are not suitable.</td><td colspan="1">Invalid inputs are properly handled, without bugs or major problems. However, there might be very few improper reactions or minor improvements needed.</td><td colspan="1">Invalid inputs are very well handled, and there is evidence of following good practices in response to different types of inputs.</td></tr>
<tr><td colspan="1">C5</td><td colspan="1">Logging, Backup and restore are not implemented, or there are major issues.</td><td colspan="1">Logging, Backup and Restore are partially implemented. There are some bugs or shortcomings.</td><td colspan="1">Logging, Backup and Restore are fully implemented. All suspicious incidents are logged. However, it could be still improved.</td><td colspan="1">Logging, Backup and Restore are complete and well formatted, and there is evidence of good practices.</td></tr>
</table>


<table><tr><th colspan="1" rowspan="2">Criteria</td><th colspan="1">Unsatisfactory</td><th colspan="1">Satisfactory</td></tr>
<tr></td><td colspan="1">L0 (0 point)</td><td colspan="1">L1 (1 point)</td></tr>
<tr><td colspan="1">C3</td><td colspan="1">The system is not secure (or partially) against SQL Injection. The SQL queries are not consistent throughout the code. There are coding bugs or issues.</td><td colspan="1">The system is fully secure against SQL Injection. Appropriate mechanism and coding practices are used. SQL queries and codes are consistent in the final product.</td></tr>
<tr><td colspan="1">C6</td><td colspan="1"><p>Students cannot properly run and demonstrate the system, or cannot explain it, or answer the technical questions.</p><p>There is no evidence of original work or satisfactory contribution by the student.</p></td><td colspan="1"><p>Students can properly run and demonstrate the system and provide relevant answers to the majority of the technical questions. </p><p>The work is evidently original, and there is evidence of sufficient contribution by the student.</p></td></tr>
</table>



<a name="_dt2c63wvy144"></a>**

|<h1>**Submission**</h1>|
| :- |
\-----
## <a name="_1sz6l2vaw2p8"></a><a name="_nk2f1zks73de"></a>**Deliverable**
The delivery to be handed in must consist of **one zip-file**, named as below: 

***studentnumber1\_studentnumber2**.**zip***

The zip-file must contain:

1. A one-page **pdf document**, called **fitplus.pdf**, containing **Names** and **student numbers** of the team (maximum **2** students per team),
1. A directory called **src**, containing all the **code files** and the **data files**, including one main file **fitplus.py**. Starting the system should be done by running **fitplus.py**.


|<p><h2><a name="_z3lssm2assd"></a>**⚠ IMPORTANT NOTES**</h2></p><p>1. **Do not** include any **bulky** Python system files in the delivery.</p><p>2. The code must **only** use **standard library modules,** plus **sqlite3**, **re** (regular expression) and any **Asynchronous cryptography** and **hash** library of your choice. </p><p>3. The code must run **error-free** (on a standard Windows or MAC PC). If needed, the code should only write to a temporary storage subfolder of the current folder, on the local machine. </p><p>4. The code should **only** write to **temporary storage** directories on the local machine, meaning on the current (running) folder or a subfolder of it.</p><p>5. We encourage you to work in a **team of 2 persons**. However, individual work is also acceptable, if you prefer to do it individually, or you are not able to make a team (e.g., retakers).</p><p>6. When working in a team, **only one team member (the team leader)** submits the assignment, and all group members submit a group-info message with names and student numbers of the entire team, clearly indicating who is the team leader.</p><p>7. Part time-students can form a group only with part-time students and full-time students are allowed to form a group with only full-time students. Retake students are free to form a team with non-retake students (the only restriction is FT with FT, and PT with PT).</p><p></p>|
| :- |

## <a name="_n0fifc5gg5eh"></a>**How to submit?**
- **Students** can only submit it via the appropriate channels in MS Teams. 

Please note that submission through chat or email is not accepted. If you confront any problem in submission, contact your teacher before the deadline to assist you. As the submission dates (first chance and second chance) are usually on weekend, it is obvious that any communication with your teacher during the weekend might not be replied. Hence, during the working days of the submission week, ensure that you know how to submit it, and everything correctly works for you. 

Please do not leave any problem or issues with your submission on the submission day, otherwise you may miss on-time submission.

## <a name="_m0urxfvhfakx"></a>**Deadline**
Submission deadline for the **First Chance** is **11 JUNE 2023.**

Submission deadline for the **Second Chance** is **TBD**.



|<h1>**Presentation**</h1>|
| :- |
## -----
The presentation will be planned within the next three weeks after the submission deadline. It is mandatory for grading.

- Each presentation (for a submission, either individual work or group submission) will be scheduled for maximum 30 minutes.
- The presentation will be placed physically in Wijnhaven 107. The room will be announced later.
- An online form will be available on 13 June, with some time slots. 

**Links of presentation scheduling form are provided on the course team on MS Teams. Ask your teacher to help if you couldn’t find it.**

A student or a group can select their preferred time slot for the presentation. Because we have a restriction to complete the grading of assignment before the end of the education year, ensure that you timely choose your preferred time slot and register your name in the form, otherwise, you have to only pick one from the remaining time slots. Although we do our best to facilitate it, but we are not sure if we can provide additional time slots, if you miss your presentation.
## **What is the presentation?**
You can see the criteria C6 in the [Grading Table](#_grading_table) and [Marking Scheme](#_marking_scheme) to see what the expectation for the presentation is.

You should run the system and demonstrate the functionalities of the system. You will be asked to explain how you have implemented the requirements of the system. You don’t need to prepare any slides for the presentation.

For example, we may ask you questions like these: how you have implemented SQL queries? Is your application secured against SQL injection attacks and why? Where have you implemented the input validation layer? Which mechanism is used in the application to implement input validation? Why you used this mechanism? Are you protecting it against buffer-overflow attack and how? Are you protecting it against Null-byte attack and how? How do you deal a user-generated and server-generated invalid inputs? How do you decide that an activity in your log is suspicious or normal? Show the data in the database (you can install a third-part software or plugin for this), Show the code for the user authentication, …

**You will be guided by your teachers during the presentation what you need to do.**
