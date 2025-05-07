import json

from dash import dcc, html

from control_room.connection import ModuleConnection
# from control_room.utils.logging import logger
from control_room.utils.logserver import logfile as log_file_path


def get_layout(
    modules: list[ModuleConnection], macros: dict | None
) -> html.Div:
    logfile = log_file_path.stem + log_file_path.suffix

    module_tiles = [] if macros is None else [create_macro_tile(macros)]
    module_tiles += [get_module_tile_layout(mod) for mod in modules]

    return html.Div(
        id="control_room_app",
        children=[
            html.Div(
                id="header_row",
                children=[
                    html.Img(
                        src="assets/images/connection-box-chart-svgrepo-com.svg",  # noqa
                        id="control_room_icon",
                        className="header_icon",
                    ),
                    html.Div(
                        "DAREPLANE Control Room", id="control_room_title"
                    ),
                    html.Div(
                        children=[
                            create_module_server_info(m) for m in modules
                        ],
                        id="module_server_check_boxes",
                    ),
                ],
            ),
            html.Div(
                id="control_room_body",
                children=[
                    # left side
                    html.Div(
                        id="lsl_and_log_div",
                        className="lsl_and_log",
                        children=[
                            get_lsl_streams_tile(),
                            get_log_stream_tile(logfile),
                        ],
                    ),
                    # right side
                    html.Div(
                        id="module_tile_div",
                        className="module_tiles",
                        children=module_tiles,
                    ),
                    # A timer for the log reading and the lsl fetch
                    dcc.Interval(
                        id="interval_3s", interval=3 * 1000, n_intervals=0
                    ),
                ],
            ),
            html.Div(id="last_pcomm_sent_div", className="hidden_div"),
            html.Div(id="last_macro_sent_div", className="hidden_div"),
        ],
    )


def create_module_server_info(module: ModuleConnection) -> html.Div:
    # this will contain a parent box which is displayed in the header row
    # and some meta info text box, which is displayed only on hover

    return html.Div(
        children=[html.Div(str(module), className="module_meta")],
        className="module_check_box",
        id=f"{module.name}_check_box",
    )


def create_macro_tile(macros: dict) -> html.Div:
    layout = html.Div(
        id="macros_div",
        className="module_tile",
        children=[
            # the header row
            html.Div(
                className="tile_header",
                children=[
                    html.Div(className="module_name", children=["Macros"])
                ],
            ),
            html.Div(
                className="tile_pcomms",
                children=[
                    get_macro_button_input_pair(mc)
                    for k, mc in macros.items()
                    if k != "globals"
                ],
            ),
        ],
    )

    return layout


def get_macro_button_input_pair(mc: dict) -> html.Div:
    default_input = ""

    print(f"\n\n {mc} \n\n")

    if "default_json" in mc.keys():
        default_input = json.dumps(mc["default_json"])

    return html.Div(
        id=f'{mc["name"]}|button_input_div',
        className="pcomm_button_input_row",
        children=[
            html.Button(
                f"{mc['name']}",
                id=f'{mc["name"]}|button',
                className="pcomm_button",
                n_clicks=0,
            ),
            dcc.Textarea(id=f'{mc["name"]}|input', value=default_input),
        ],
    )


def get_lsl_streams_tile() -> html.Div:
    return html.Div(
        id="lsl_stream_tile",
        className="tile",
        children=[
            html.Div(
                children=[
                    html.Img(
                        src="assets/images/flows-1-svgrepo-com.svg",
                        className="header_icon",
                        id="lsl_title_icon",
                    ),
                    html.Div(
                        "LSL Streams",
                        id="lsl_streams_title",
                        className="tile_header",
                    ),
                ],
                id="lsl_tile_header",
            ),
            html.Div(id="lsl_streams_list"),
        ],
    )


def get_log_stream_tile(logfile_name: str) -> html.Div:
    return html.Div(
        id="log_stream_tile",
        className="tile",
        children=[
            html.Div(
                children=[
                    html.Img(
                        src="assets/images/log-file-format-svgrepo-com.svg",
                        className="header_icon",
                        id="logfile_title_icon",
                    ),
                    html.Div(
                        f"Logfile - {logfile_name}",
                        id="logfile_title",
                        className="tile_header",
                    ),
                ],
                id="log_stream_tile_header",
            ),
            html.Div(id="logfile_data"),
        ],
    )


def get_module_tile_layout(module: ModuleConnection) -> html.Div:
    return html.Div(
        id=f"{module.name}_tile",
        className="module_tile tile",
        children=[
            # the header row
            html.Div(
                className="tile_header",
                children=[
                    html.Div(
                        className="module_name", children=[f"{module.name}"]
                    ),
                    html.Div(className="module_ip", children=[f"{module.ip}"]),
                    html.Div(
                        className="module_port", children=[f"{module.port}"]
                    ),
                    html.Div(
                        className=f"module_type module_{module.type}",
                        children=[f"{module.type}:{module.near_port}"],
                    ),
                ],
            ),
            # the pcommand button input pairs
            html.Div(
                className="tile_pcomms",
                children=[
                    get_pcomm_button_input_pair(pc, module.name, module)
                    for pc in module.pcomms
                ],
            ),
        ],
    )


def get_pcomm_button_input_pair(
    pcomm_name: str, mod_name: str, conn: ModuleConnection
) -> html.Div:
    # logger.debug(f"Building button input for {pcomm_name=} {mod_name=}")
    defaults = ""
    if "ao-communication" in mod_name:
        defaults = conn.pcomms_defaults[pcomm_name]

    return html.Div(
        id=f"{mod_name}|{pcomm_name}|button_input_div",
        className="pcomm_button_input_row",
        children=[
            html.Button(
                f"{pcomm_name}",
                id=f"{mod_name}|{pcomm_name}|button",
                className="pcomm_button",
                n_clicks=0,
            ),
            dcc.Textarea(
                id=f"{mod_name}|{pcomm_name}|input",
                className="module_input",
                value=defaults,
            ),
        ],
    )
