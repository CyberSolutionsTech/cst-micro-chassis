from cst_micro_chassis.logging import get_log_config_dict


def test_logging_simple():
    app_name = 'new_restful_api'
    conf_dict = get_log_config_dict(app_name)
    assert app_name in conf_dict['loggers'].keys()

    assert conf_dict['loggers'][app_name]['level'] == 'INFO'
