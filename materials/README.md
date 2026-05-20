# Project Backend 04 — Python_Bootcamp

**Summary:**  
In this project, you will learn how to add databases to web applications in Python using Flask and work with authorization.

💡 [Click here](https://new.oprosso.net/p/4cb31ec3f47a4596bc758ea1861fb624) to share your feedback on this project. It’s anonymous and helps our team improve the learning experience. We recommend completing the survey immediately after finishing the project.

## Contents

  - [Chapter I](#chapter-i)
    - [Instructions](#instructions)
  - [Chapter II](#chapter-ii)
    - [General Information](#general-information)
      - [Authorization](#authorization)
      - [Identification, Authentication, Authorization](#identification-authentication-authorization)
      - [Authorization Using Login and Password](#authorization-using-login-and-password)
    - [Topics to Study](#topics-to-study)
  - [Chapter III](#chapter-iii)
    - [Task 1. Adding a Database](#task-1-adding-a-database)
    - [Task 2. Adding Authorization](#task-2-adding-authorization)
    - [Task 3. Adding Game Logic for Two Players](#task-3-adding-game-logic-for-two-players)

## Chapter I

### Instructions

1. Throughout the course, you will often feel uncertain and have limited information, but that's all part of the experience. Remember, the repository and Google are always there for you. So are your peers and Rocket.Chat. Talk. Search. Use your common sense. Don't be afraid to make mistakes.
2. Be mindful of your sources. Cross-check. Think critically. Analyze. Compare.
3. Read the tasks carefully, and then read them again.
4. Pay close attention to the examples, too. They may include information that is not explicitly stated in the task itself.
5. You may encounter inconsistencies when something in the task or example contradicts what you thought you knew. Try to figure them out. If you can't, write it down as an open question and resolve it as you go. Don't leave questions unresolved.
6. If a task seems unclear or impossible, it probably just feels that way. Break it down into parts. Most of them will make sense on their own.
7. You’ll encounter all kinds of tasks. The bonus ones are for those who are curious and detail-oriented. They’re optional and more challenging, but completing them gives you extra experience and insight.
8. Don't try to cheat the system or your peers. Ultimately, you'll only be cheating yourself.
9. Got a question? Ask the peer to your right. If that doesn't help, ask the peer to your left.
10. When asking for help, always make sure you understand the why, how, and what-for. Otherwise, the help won't be very useful.
11. Always push your code to the develop branch only. The master branch will be ignored. Work inside the src directory.
12. Your directory should not contain any files besides those required for the tasks.

## Chapter II

### General Information

#### Authorization

Authorization tools control access of legitimate users to system resources, granting each user only the rights assigned by the administrator.

#### Identification, Authentication, Authorization

- **Identification** is the process by which a subject’s unique identifier is established, unambiguously defining them within an information system.
- **Authentication** is the procedure of verifying authenticity — for example, validating a user by comparing the entered password with the stored password in the system.
- **Authorization** is the granting of rights to a specific individual or group to perform a defined set of actions.

#### Authorization Using Login and Password

This method is based on the user providing a login and password for successful identification and authentication within the system. The login-password pair is set by the user during registration. Upon successful authorization, the server grants the user rights to perform permitted requests.  
The client sends a request to the server and receives an "Unauthorized" message along with information on how to authorize. After successful authorization, each subsequent client request automatically includes an Authorization header ([authorization header formation](https://datatracker.ietf.org/doc/html/rfc7617)), which carries client credentials for server authentication.

![auth_eng](misc/images/Auth_ENG.png)

[Other methods of authorization](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#authentication_schemes) also exist.

### Topics to Study

- Web application,
- Authorization using login and password pair (basic auth),
- PostgreSQL,
- Flask,
- SQLAlchemy.

## Chapter III

## Project: Tic-Tac-Toe
Use the backend project from last week’s T03.

### Task 1. Adding a Database

- Define the connection to a PostgreSQL database using SQLAlchemy.
- Remove the storage class.
- Add appropriate annotations to class parameters that need to be persisted in the database.

### Task 2. Adding Authorization

- Add users with UUID, login, and password.
- Implement user support across all layers.
- Create a SignUpRequest model containing login and password.
- Create an authorization service that uses UserService:
  - a registration method that accepts a SignUpRequest and returns a success status;
  - an authorization method that accepts login and password encoded in Base64 (login:password) in the header and returns the user’s UUID.
- Create an authorization controller with the following endpoints:
  - user registration;
  - user authorization (login).
- Create a UserAuthenticator structure that protects against requests from unauthorized users:
  - validate login and password;
  - if validation succeeds, process the request;
  - if validation fails, respond with status code 401 and do not process the request.
- Apply UserAuthenticator to your endpoints:
  - allow unauthenticated access to registration and authorization endpoints;
  - require authorization for all other endpoints.

### Task 3. Adding Game Logic for Two Players

- Add states for the current game:
  - Waiting for players;
  - Player’s turn with UUID;
  - Draw;
  - Victory for player with UUID.
- Add information about the marks (symbols) that users will use during the game.
- Improve the game-ending logic using the defined states.
- Add an endpoint for creating a new game with either a user or the computer.
- Add an endpoint to retrieve available current games.
- Add an endpoint for a user to join a game.
- Improve the endpoint for updating the current game, considering whether the opponent is a user or the computer.
- Add an endpoint to retrieve the current game.
- Add an endpoint to retrieve user information by UUID.