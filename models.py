#!/usr/bin/env python
# encoding: utf-8

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

# Game Models
class User(ndb.Model):
    """User Profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    score = ndb.IntegerProperty(required=True, default=0)

class Game(ndb.Model):
    """Game Object"""
    target = ndb.StringProperty(required=True)
    current_result = ndb.StringProperty(required=True)
    attempts = ndb.IntegerProperty(required=True)
    max_attempts = ndb.IntegerProperty(required=True, default=6)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    guesses = ndb.StringProperty(repeated=True)
    result_history = ndb.StringProperty(repeated=True)

    @classmethod
    def new_game(cls, user_key, word):
        current_result = "".join(["_" for i in range(0, len(word))])
        game = Game(user=user_key,
                    target=word.upper(),
                    current_result=current_result,
                    attempts=0,
                    max_attempts=6,
                    game_over=False,
                    parent=user_key)
        game.put()
        return game

    def end_game(self, won=False):
        self.game_over = True
        self.put()

        score = self.max_attempts - self.attempts
        record = GameRecord(user=self.user,
                      date=date.today(),
                      won=won,
                      score=score,
                      parent=self.user)
        record.put()

        user = self.user.get()
        user.score += score
        user.put()

    def to_form(self, message):
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts = self.attempts
        form.current_result = self.current_result
        form.game_over = self.game_over
        form.message = message
        return form

class GameRecord(ndb.Model):
    """gameRecord object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    score = ndb.IntegerProperty(required=True)


# Forms
class GameForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)
    attempts = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    current_result = messages.StringField(4, required=True)
    message = messages.StringField(5, required=True)
    user_name = messages.StringField(6, required=True)

class GameForms(messages.Message):
    items = messages.MessageField(GameForm, 1, repeated=True)

class NewGameForm(messages.Message):
    user_name = messages.StringField(1, required=True)
    word = messages.StringField(2, required=True)

class MakeMoveForm(messages.Message):
    guess = messages.StringField(1, required=True)

class GetHightScoresForm(messages.Message):
    number_of_results = messages.IntegerField(1, required=False)

class ScoreForm(messages.Message):
    user_name = messages.StringField(1, required=True)
    score = messages.IntegerField(2, required=True)

class ScoreForms(messages.Message):
    items = messages.MessageField(ScoreForm, 1, repeated=True)

class UserRankingForm(messages.Message):
    name = messages.StringField(1, required=True)
    win_ratio = messages.FloatField(2, required=True)

class UserRankingForms(messages.Message):
    items = messages.MessageField(UserRankingForm, 1, repeated=True)

class CancelGameForm(messages.Message):
    success = messages.BooleanField(1, required=True)
    message = messages.StringField(2, required=True)

class MoveHistoryForm(messages.Message):
    guess = messages.StringField(1, required=True)
    result = messages.StringField(2, required=True)

class MoveHistoryForms(messages.Message):
    items = messages.MessageField(MoveHistoryForm, 1, repeated=True)

class StringMessage(messages.Message):
    message = messages.StringField(1, required=True)

