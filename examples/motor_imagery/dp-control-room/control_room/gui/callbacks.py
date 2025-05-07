import ast
import json
import re
from pathlib import Path
from time import sleep

import pylsl
from dash import Dash, ctx, html
from dash.dependencies import Input, Output, State

from control_room.connection import ModuleConnection
from control_room.utils.logging import logger
from control_room.utils.logserver import logfile as log_file_path


class PayloadError(KeyError):
    pass


def add_callbacks(
    app: Dash, modules: list[ModuleConnection], macros: dict | None = None
) -> Dash:
    """Add callbacks to a given app"""
    logfile = log_file_path

    # Stats update will refresh the log content, lsl stream and module state
    app = add_stats_update(app, logfile, modules)
    app = add_json_verification_cb(app, modules=modules, macros=macros)
    app = add_pcomm_sender(app, modules)

    if macros is not None:
        app = add_macros_sender(app, modules, macros)
        logger.debug("Added macros callback")
        # macro_buttons = {f"{mc['name']}":
        #                  Input(f"{mc['name']}|button", 'n_clicks')
        #                  for mc in macros.values()}

        # print(f"{macro_buttons=}")

    return app


def test_button_bc(app):
    @app.callback(
        output=Output("last_macro_sent_div", "children"),
        inputs=Input("START_RECORDINGS|button", "n_clicks"),
    )
    def print_pressed(all_btns):
        msg = f"{all_btns=}"
        logger.warning(msg)

        return msg

    return app


def add_json_verification_cb(
    app: Dash, modules: list[ModuleConnection], macros: dict | None
) -> Dash:
    """Check the json strings in each inbox"""

    model_input_ids = [
        f"{mconn.name}|{pcomm}|input" for mconn in modules for pcomm in mconn.pcomms
    ]

    if macros is not None:
        macros_input_ids = [
            f"{mc['name']}|input" for k, mc in macros.items() if k != "globals"
        ]
        all_ids = model_input_ids + macros_input_ids
    else:
        all_ids = model_input_ids

    outputs = [Output(op, "className") for op in all_ids]
    inputs = [Input(op, "value") for op in all_ids]
    states = [State(op, "className") for op in all_ids]

    @app.callback(output=outputs, inputs=inputs, state=states)
    def check_jsonifyable(*args):
        rets = [v for v in ctx.states.values()]  # states

        # Only check the triggering input
        inp_name = ctx.triggered[0]["prop_id"]
        inp = ctx.inputs.get(inp_name, None)

        if inp is None:
            return rets

        # get the index of the changing also in the output - only possible
        # as inputs and outputs are generated with the same order
        idxinp = list(ctx.inputs.keys()).index(inp_name)

        if inp is not None and inp != "":
            try:
                json.loads(str(inp))
                rets[idxinp] = "valid_json_input"
                # logger.debug(f"{inp=} is valid")
            # except Exception as e:
            # print(f">>>>> {e=}")
            except json.JSONDecodeError:
                rets[idxinp] = "invalid_json_input"
                # logger.debug(f"{inp=} is invalid")

        return rets

    return app


def add_macros_sender(
    app: Dash,
    modules: list[ModuleConnection],
    macros: dict,
) -> Dash:
    modules_dict = {module.name: module for module in modules}
    macro_name_key_map = {v["name"]: k for k, v in macros.items() if k != "globals"}
    macro_buttons = {
        f"{mc['name']}": Input(f"{mc['name']}|button", "n_clicks")
        for k, mc in macros.items()
        if k != "globals"
    }

    globals = macros.get("globals", None)
    sleep_s = globals.get("sleep_s", None) if globals else None

    logger.debug(f"{macro_buttons=}")

    @app.callback(
        output=Output("last_macro_sent_div", "children"),
        inputs={"all_buttons": macro_buttons},
        state={
            "all_states": {
                f"{mc['name']}": State(f"{mc['name']}|input", "value")
                for k, mc in macros.items()
                if k != "globals"
            }
        },
    )
    def send_macro(all_buttons, all_states):
        logger.debug(f"Send macro activated: {all_buttons=}")
        button_id = ctx.triggered_id if not None else "No clicks yet"
        msgs = ""

        if ctx.triggered_id is not None:
            m_name, _ = button_id.split("|")
            mc = macros[macro_name_key_map[m_name]]
            if "delay_s" in mc.keys():
                sleep(mc["delay_s"])

            if all_states[m_name] != "":
                json_dict = ast.literal_eval(all_states[m_name])
                m_kwargs = evaluate_templates(json_dict)
            else:
                m_kwargs = {}

            logger.debug(f"Macro details: {m_name=}, {mc=}, {m_kwargs=}")

            for cmn, cm_list in mc["cmds"].items():
                if sleep_s:
                    logger.debug(f"Sleeping for {sleep_s=}")
                    sleep(sleep_s)

                module = modules_dict[cm_list[0]]

                msg = cm_list[1]

                json_payload = {}
                for mapping in cm_list[2:]:
                    k2, k1 = mapping.split("=")
                    if k1 not in m_kwargs.keys():
                        error_msg = f"Key '{k1}' not in provided payload"
                        logger.error(error_msg)
                        raise PayloadError(error_msg)

                    json_payload[k2] = m_kwargs[k1]

                if json_payload != {}:
                    payload_str = json.dumps(json_payload).replace("'", '"')

                    # TODO: Properly refactor the AO module that this extra
                    # handling is no longer needed!
                    if json_payload is not None and "ao-communication" in module.name:
                        payload_str = make_ao_payload_from_json(payload_str)

                    msg = msg + "|" + payload_str

                logger.debug(
                    f"Sending {msg=} to {module.name}@{module.ip}:" f"{module.port}"
                )
                if ";" in msg:
                    logger.error(
                        f"Found a semi-colon in {msg=} - this is a reserved character please use characters other than `;`"
                    )
                if "ao-communication" in module.name:
                    # keep the old message structure until the AO module
                    # is properly integrated
                    module.socket_c.sendall(msg.encode())
                    msg = msg + ";"
                else:
                    msg = msg + ";"  # add semi-colon to separate commands
                    module.socket_c.sendall(msg.encode())

                msgs += msg

        return msgs

    return app


def evaluate_templates(d: dict) -> dict:
    """If a dictionary contains $<some_name> templates in its values,
    replace them with the variable"""
    for k, v in d.items():
        if isinstance(v, str):
            keys = re.findall("\$<([^>]*)>", v)

            for kk in keys:
                v = v.replace(f"$<{kk}>", str(d[kk]))

            d[k] = v

    return d


def add_pcomm_sender(app: Dash, modules: list[ModuleConnection]) -> Dash:
    modules_dict = {module.name: module for module in modules}

    @app.callback(
        output=Output("last_pcomm_sent_div", "children"),
        inputs={
            "all_buttons": {
                f"{mconn.name}|{pcomm}": Input(
                    f"{mconn.name}|{pcomm}|button", "n_clicks"
                )
                for mconn in modules
                for pcomm in mconn.pcomms
            }
        },
        state={
            "all_states": {
                f"{mconn.name}|{pcomm}": State(f"{mconn.name}|{pcomm}|input", "value")
                for mconn in modules
                for pcomm in mconn.pcomms
            }
        },
    )
    def send_pcomm(all_buttons, all_states):
        button_id = ctx.triggered_id if not None else "No clicks yet"
        msg = ""

        if ctx.triggered_id is not None:
            mod_name, pcomm_name, _ = button_id.split("|")
            module = modules_dict[mod_name]
            msg = pcomm_name

            # TODO - think of a way to validate the string (potentially a different callback) which is triggered upon entering the text values # noqa
            json_payload = all_states[f"{mod_name}|{pcomm_name}"]
            logger.debug(f"module button {json_payload=}")

            if json_payload is not None and "ao-communication" in module.name:
                json_payload = make_ao_payload_from_json(json_payload)
                # import pdb
                # pdb.set_trace()

            if json_payload:
                msg = msg + "|" + json_payload

            logger.debug(
                f"Sending {msg=} to {module.name}@{module.ip}:" f"{module.port}"
            )
            module.socket_c.sendall(msg.encode())

        return msg

    return app


def add_stats_update(app: Dash, logfile: Path, modules: list[ModuleConnection]) -> Dash:
    mod_outputs = [Output(f"{m.name}_check_box", "className") for m in modules]

    @app.callback(
        output=[
            Output("lsl_streams_list", "children"),
            Output("logfile_data", "children"),
        ]
        + mod_outputs,
        inputs=[Input("interval_3s", "n_intervals")],
    )
    def print_setting(n):
        lsl_stream_msg = [html.P("> " + s.name()) for s in pylsl.resolve_streams()]

        # there is far mre officient ways of reading tail
        # but for now this is sufficient (500us at 100k)
        if logfile.exists():

            # The version with paragraphs to a list failed - stop it for now
            # as it would only add color to the GUI
            log_str_msg = []

            with open(logfile, "r") as logf:
                # logger.debug("Trying to add colored log")
                lines = logf.readlines()[-25:]
                for logline in lines:

                    llevel = re.search(r"(DEBUG|INFO|WARNING|ERROR)", logline)
                    log_level = llevel.group(1) if llevel else "DEBUG"

                    # log_level is used for coloring with css, use DEBUG as default
                    log_str_msg.append(html.P(logline, className=f"{log_level}"))

            log_str_msg = log_str_msg[::-1]
        else:
            log_str_msg = f"No logfile at {logfile}"

        # check corrent up state
        mod_class_names = []
        classes = {
            "success": "module_check_box running_module_check_box",
            "fail": "module_check_box",
        }
        mod_class_names = [classes["success"]] * len(modules)

        # for m in modules:
        #     try:
        #         ret = m.socket_c.sendall('UP')
        #         if ret == 1:
        #             mod_class_names.append(classes['success'])
        #         else:
        #             mod_class_names.append(classes['fail'])
        #     except Exception as e:
        #         logger.debug(f"Failed communicating with {m.name} @ {m.ip}"
        #                      f":{m.port} - {e=}")
        #         mod_class_names.append(classes['fail'])
        #

        return [lsl_stream_msg, log_str_msg] + mod_class_names

    return app


def make_ao_payload_from_json(json_payload: str | None) -> str | None:
    """Transform a json string to pipe separated list of values only"""

    if json_payload is None or json_payload == "":
        return None

    d = json.loads(json_payload)
    lstr = (
        str(list(d.values()))
        .replace("'", "")
        .replace(",", "|")
        .replace(" ", "")
        .replace("[", "")
        .replace("]", "")
    )

    # For the json to be valid, we need double backslashes, for AO however, it needs to be single
    lstr = lstr.replace("\\\\", "\\")

    return lstr
