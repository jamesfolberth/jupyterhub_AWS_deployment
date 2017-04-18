"""
A simple subclass of LocalGoogleOAuthenticator that strips off the @domain.com
portion of a username, allowing us to create valid system usernames.
"""

import oauthenticator

class LocalGoogleOAuthenticator(oauthenticator.LocalGoogleOAuthenticator):
    def normalize_username(self, username):
        """Normalize the given username and return it

        Override in subclasses if usernames need different normalization rules.

        The default attempts to lowercase the username and apply `username_map` if it is
        set.
        """
        username = username.split('@')[0].lower()
        username = self.username_map.get(username, username)
        return username

