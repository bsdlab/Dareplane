from pathlib import Path

from dash import Dash

from control_room.connection import ModuleConnection
from control_room.gui.callbacks import add_callbacks
from control_room.gui.layout import get_layout


def build_app(modules: list[ModuleConnection], macros: dict | None) -> Dash:
    app = Dash(__name__, external_stylesheets=["assets/styles.css"])
    app.layout = get_layout(modules, macros=macros)

    # attach callbacks
    app = add_callbacks(app, modules=modules, macros=macros)

    return app
