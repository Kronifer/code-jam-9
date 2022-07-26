from websockets import WebsocketsCommonProtocol


class Connections:
    """
    Class for managing WebsocketsCommonProtocol instances

    Records a group of WebsocketsCommonProtocol objects in a dict, keyed to
    usernames. Implements adding and removing users and tracks the most
    recently added and most recently departed users.
    """

    def __init__(self, data: dict = None, user_limit: int = None) -> None:
        """Initialize class"""
        self.data = {} if data is None else data
        self._user_limit = user_limit
        self._latest_departed_user = self._newest_user = None

    def __len__(self) -> int:
        """Returns number of current users"""
        return len(self.data)

    def __str__(self) -> str:
        """Returns string representation of class dict"""
        return str(self.data)

    def __repr__(self) -> str:
        """Returns string representation of class dict"""
        return str(self)

    @property
    def user_limit(self) -> None | int:
        """Returns current user limit"""
        return self._user_limit

    @user_limit.setter
    def user_limit(self, value: int) -> None:
        """Sets user limit to a value. Does not perform validation"""
        self._user_limit = value

    @property
    def user_count(self) -> int:
        """
        User count property

        Returns `_user_count`, which contains the number of users before
        at the last update
        """
        return self._user_count

    def update_user_count(self) -> None:
        """Updates user count by checking length of the class dict"""
        self._user_count = len(self)

    @property
    def latest_departed_user(self) -> None | str:
        """
        Latest departed user property

        Returns username of most recently departed user, None if no one has
        left yet
        """
        return self._last_departed_user

    @property
    def newest_user(self) -> None | str:
        """
        Newest user property

        Returns username of most recently joined user,
        None if no one has joined yet
        """
        return self._newest_user

    def has_user(self, uname: str) -> bool:
        """Determines whether a username is in use"""
        return uname in self.data.keys()

    def add_user(
        self,
        uname: str,
        value: WebsocketsCommonProtocol,
        require_unique=False,
    ) -> None | "Connections":
        """
        Method to add new user with a given username

        Adds a username-WebsocketsCommonProtocol pair to class dict,
        optionally raising an error instead of overwriting an existing user.
        Records username in `newes_user` on success
        """
        if self.has_user(uname) and require_unique:
            raise KeyError(f"username {uname} already in use")
        self.data[uname] = value
        self._newest_user = uname
        return self

    def remove_user(
        self, uname: str, raise_error: bool = False
    ) -> None | "Connections":
        """
        User deletion method

        Deletes user by name, optionally raising an error if no user has_user
        has that name. Records username in `last_departed_user`.
        """
        if self.has_user(uname):
            del self.data[uname]
            self._last_departed_user = uname
        elif raise_error:
            raise KeyError(f"No user named {uname}")
        return self
