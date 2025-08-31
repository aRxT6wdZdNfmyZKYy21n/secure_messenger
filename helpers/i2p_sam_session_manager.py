from helpers.i2p_sam_session import (
    I2PSAMSession,
)


class I2PSAMSessionManager(object):
    __slots__ = (
        '__session_by_name_map',
    )

    def __init__(
            self
    ) -> None:
        super().__init__()

        self.__session_by_name_map: dict[str, I2PSAMSession] = {}

    def create_session(
            self
    ) -> I2PSAMSession:
        session = I2PSAMSession()
        session_by_name_map = self.__session_by_name_map

        session_name = session.get_name()

        assert session_name not in session_by_name_map, (
            session_name,
        )

        session_by_name_map[session_name] = session

        return session

    async def remove_session(
            self,

            session_name: str
    ) -> None:
        session = self.__session_by_name_map.pop(
            session_name,
        )

        await session.fini()
