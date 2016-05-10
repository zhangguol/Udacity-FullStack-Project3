#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.api import mail, app_identity
from api import HangmanApi

from models import User, Game

class SendRemiderEmail(webapp2.RequestHandler):
    def get(self):
        users = User.query(User.email != None)

        def _has_active_game(user):
            games = Game.query(ancestor=user.key).filter(Game.game_over == False)
            return games.count() > 0

        users_has_active_game = filter(_has_active_game, users)

        app_id = app_identity.get_application_id()
        for user in users_has_active_game:
            subject = 'This is a reminder1'
            body = 'Hello {}, you have an incomplete Hangman game!'.format(user.name)
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)




app = webapp2.WSGIApplication([('/crons/send_reminder', SendRemiderEmail)], debug=True)
