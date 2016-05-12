# Full Stack Nanodegree Project 4 -- Hangman

## Set-Up Instructions 

1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
2.  Run the app with the devserver using dev_appserver.py DIR, or using GoogleAppEngineLaucher,
and ensure it's running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
3.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.


## Game Description:
Hangman is a simple guessing game. Each game begins with a target word, and a maximum number of
'max_attempts' (optional, default is 6). At first, The word to guess is represented by a row of dashes,
representing each letter of the word. 'Guesses' are sent to the 'make_move' endpoint which will
replay with current game status. If the guessing player suggests a letter which occurs in the word,
the letter will be in all its correct positions. If the suggested letter or number does not occur
in the word, the current apptempt time 'attempts' will be increased 1. If the 'attempts' is equal to
the 'max_attempts', the game will be over.


## Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.


## Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, word
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. word is the target word 

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess' and returns the updated state of the game.
    If this causes a game to end, a score will be updated for the user, and a
    GameRecord will be created.
   
- **get_user_games**
    - Path: 'get_user_games'
    - method: POST
    - Parameters: user_name
    - Returns: GameForms
    - Description: Get all active of the given user. Will raise a NotFoundException
    if a User with that user_name doesn't exist.

- **cancel_game**
    - Path: 'cancel/{urlsafe_game_key}'
    - method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: CancelGameForm
    - Description: Cancel the game with the given urlsafe_game_key if the game is active.

- **get_high_scores**
    - Path: 'get_high_scores'
    - method: POST
    - Parameters: number_of_results(otional)
    - Returns: ScoreForms
    - Description: Get the scores in descending order. If there is number_of_results, the
    limits number of results will be returned.

- **get_user_rankings**
    - Path: 'get_user_rankings'
    - method: GET
    - Parameters: None
    - Returns: UserRankingForms
    - Description: Get the rankings of the users by the win/lose ratio.

