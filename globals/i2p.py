from helpers.i2p_sam_session_manager import (
    I2PSAMSessionManager,
)


__all__ = (
    'g_i2p_globals',
)


class I2PGlobals(object):
    __slots__ = (
        '__sam_session_manager',
    )

    def __init__(self) -> None:
        super().__init__()

        self.__sam_session_manager = I2PSAMSessionManager()

    def get_sam_session_manager(self) -> I2PSAMSessionManager:
        return self.__sam_session_manager


g_i2p_globals = I2PGlobals()
