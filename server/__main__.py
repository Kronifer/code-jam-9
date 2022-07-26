import asyncio
import json

import websockets


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
        value: websockets.WebsocketsCommonProtocol,
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


CONNECTIONS = Connections()


async def request_uname(ws) -> str:
    """Requests a newly connected client's username."""
    await ws.send('{"event": "uname_request"}')
    uname = json.loads(await ws.recv())["uname"]
    if uname in CONNECTIONS.data.keys():
        await ws.send('{"error": "username already used"}')
        await request_uname(ws)
    CONNECTIONS.add_user(uname, ws)
    return uname


async def request_user_limit(ws) -> None:
    """Requests the user limit for the game from the first user who connects."""
    await ws.send('{"event": "ulimit_request"}')
    ulimit = json.loads(await ws.recv())["ulimit"]
    if ulimit < 2 or ulimit % 1 != 0:
        await ws.send('{"error": "ulimit must be an integer greater than 1"}')
        await request_user_limit(ws)
    CONNECTIONS.user_limit = ulimit


async def connect(ws) -> None:
    """
    Websocket connection handler.

    Prompts for a username after checking
    if more users can join, then waits to remove the user when they user_leave
    """
    if len(CONNECTIONS) >= CONNECTIONS.user_limit:
        await ws.send('{"error": "user limit has been reached"}')
        await ws.close()
        return
    uname = await request_uname(ws)
    # This property is initialized to None, so this reliably checks if it has to be requested
    if CONNECTIONS.user_limit is None:
        await request_user_limit(ws)
    try:
        await ws.wait_closed()
    finally:
        CONNECTIONS.remove_user(uname)


async def send_user_count_event() -> None:
    """Sends user count events to all websockets."""
    while True:
        user_count = CONNECTIONS.user_count
        if user_count != len(CONNECTIONS):
            # A user joined
            if user_count < len(CONNECTIONS):
                websockets.broadcast(
                    CONNECTIONS.data.values(),
                    f'{{"event": "user_join", "count": {user_count}, "uname": "{CONNECTIONS.newest_user}"}}',
                )
            # A user left
            else:
                websockets.broadcast(
                    CONNECTIONS.data.values(),
                    f'{{"event": "user_leave", "count": {user_count}, "uname": "{CONNECTIONS.latest_departed_user}"}}',
                )

            CONNECTIONS.update_user_count()
        await asyncio.sleep(1)


async def main():
    """Runs the websockets server."""
    async with websockets.serve(connect, "localhost", 8081):
        await send_user_count_event()


if __name__ == "__main__":
    asyncio.run(main())
