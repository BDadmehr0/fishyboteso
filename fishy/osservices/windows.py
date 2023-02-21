from typing import Tuple

from fishy.osservices.os_services import IOSServices


class Windows(IOSServices):
    def hide_terminal(self):
        pass

    def create_shortcut(self):
        pass

    def get_documents_path(self) -> str:
        pass

    def is_admin(self) -> bool:
        pass

    def get_eso_config_path(self) -> str:
        pass

    def is_eso_active(self) -> bool:
        pass

    def get_monitor_rect(self):
        pass

    def get_game_window_rect(self) -> Tuple[int, int, int, int]:
        pass
