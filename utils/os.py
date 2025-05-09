import os
import os.path


class OsUtils(object):
    __slots__ = ()

    @staticmethod
    def get_path(
            path: str
    ) -> str:
        pyi_application_home_directory_path = (
            os.getenv(
                '_PYI_APPLICATION_HOME_DIR'
            )
        )

        if pyi_application_home_directory_path:
            path = (
                os.path.join(
                    pyi_application_home_directory_path,
                    path
                )
            )

        return (
            path
        )