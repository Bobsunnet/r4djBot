__all__ = [
    "contacts_router",
    "unknown_command_router",
    "help_router",
    "manager_router",
    "order_router",
    "register_router",
    "details_router",
    "start_router",
    "user_private_router",
]

from .contacts import contacts_router
from .error_commands import unknown_command_router
from .help import help_router
from .manager_private import manager_router
from .order import order_router
from .register import register_router
from .show_details import details_router
from .start import start_router
from .user_private import user_private_router
