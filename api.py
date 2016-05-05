#!/usr/bin/env python
# encoding: utf-8

import re
import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, GameRecord
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    GameRecordForms, GameForms, CancelGameForm, GetHightScoresForm, ScoreForms,\
    ScoreForm
from util import get_by_urlsafe

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
GET_USER_GAMES_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),)
CANCEl_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),)
GET_HIGHT_SCORES_REQUEST = endpoints.ResourceContainer(GetHightScoresForm,)

@endpoints.api(name='hangman', version='v1')
class HangmanApi(remote.Service):
    """Game API"""

    # Create a new user
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='Post')
    def create_user(self, request):
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A user with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(
            message='User {} created!'.format(request.user_name))

    # Start a new game
    @endpoints.method(request_message=NEW_GAME_REQUEST,
               response_message=GameForm,
               path='game',
               name='new_game',
               http_method='POST')
    def new_game(self, request):
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A user with that name does not exist')
        game = Game.new_game(user.key, request.word)

        return game.to_form('Good luck playing Hangman')

    # Get a game status
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a Guess')
        else:
            raise endpoints.NotFoundException('Game not found!')


    # Make a move
    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')

        if game.game_over:
            return game.to_form('Game already over!')

        guess = request.guess.upper()
        if len(guess) != 1:
            raise endpoints.BadRequestException('Guess can only be one character')

        indexes= [m.start() for m in re.finditer(guess, game.target)]
        if len(indexes) > 0:
            currentResultList = list(game.current_result)
            for idx in indexes:
                currentResultList[idx] = guess
            game.current_result = "".join(currentResultList)
            game.put()
            if game.current_result == game.target:
                game.end_game(True)
                return game.to_form('You win!')
            else:
                return game.to_form('You get a correct character')
        else:
            game.attempts += 1
            game.put()
            if game.attempts >= game.max_attempts:
                game.end_game(False)
                return game.to_form("Game over! The correct word is " + game.target)
            else:
                return game.to_form("Your guess is wrong!")


    # get all of a user's active game
    @endpoints.method(request_message=GET_USER_GAMES_REQUEST,
                      response_message=GameForms,
                      path='get_user_games',
                      name='get_user_games',
                      http_method='POST')
    def get_user_games(self, request):
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A user with that name does not exist!')
        games = Game.query(ancestor=user.key).filter(Game.game_over == False)
        items = [game.to_form("") for game in games]
        return GameForms(items=items)


    # cancel a game in progress
    @endpoints.method(request_message=CANCEl_GAME_REQUEST,
                      response_message=CancelGameForm,
                      path='cancel_game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')

        if game.game_over:
            return CancelGameForm(success=False,
                                  message='Cancelling a completed game is not allowed')

        game.key.delete()
        return CancelGameForm(success=True,
                             message='Game is cancelled successfully')


    # high scores in descending order
    @endpoints.method(request_message=GET_HIGHT_SCORES_REQUEST,
                      response_message=ScoreForms,
                      path='get_high_scores',
                      name='get_high_scores',
                      http_method='POST')
    def get_high_scores(self, request):
        users = User.query().order(-User.score)
        if request.number_of_results:
            users = users.fetch(request.number_of_results)

        if not users:
            raise endpoints.NotFoundException('There is no user!')
        items = [ScoreForm(user_name=user.name, score=user.score) for user in users]

        return ScoreForms(items=items)

api = endpoints.api_server([HangmanApi])

