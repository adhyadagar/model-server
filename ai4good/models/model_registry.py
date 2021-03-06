from ai4good.models.cm.cm_model import CompartmentalModelStochastic
from ai4good.models.cm.initialise_parameters import Parameters
from ai4good.models.cm.cm_model import CompartmentalModel
from ai4good.models.nm.nm_model import NetworkModel
from ai4good.models.nm.initialise_parameters import Parameters as NMParameters
from ai4good.models.abm.np_impl.parameters import Parameters as ABMParameters
from ai4good.models.abm.np_impl.abm_model import ABM
from typing import Dict, Any
import json


def get_models() -> Dict[str, Any]:
    return {
        CompartmentalModel.ID: lambda ps: CompartmentalModel(ps),
        CompartmentalModelStochastic.ID: lambda ps: CompartmentalModelStochastic(ps),
        ABM.ID: lambda ps: ABM(ps),
        NetworkModel.ID: lambda ps: NetworkModel(ps)
    }


def create_params(ps, _model, _profile, user_input_parameters, overrides=None):  # model specific params
    """
    :param ps:
    :param _model:
    :param _profile: str or pd.Dataframe
    :param user_input_parameters: str (json object):
    :param overrides:
    :return:
    """
    if _model == CompartmentalModel.ID or _model == CompartmentalModelStochastic.ID:
        override_dct = {} if overrides is None else json.loads(overrides)
        profile_df = ps.get_params(_model, _profile) if (
            type(_profile) is str) else _profile
        if len(profile_df) == 0:
            raise ValueError('Unknown profile: '+_profile)
        return Parameters(ps, user_input_parameters, profile_df, override_dct)
    elif _model == ABM.ID:
        override_dct = {} if overrides is None else json.loads(overrides)
        profile_df = ps.get_params(_model, _profile) if (
            type(_profile) is str) else _profile
        if len(profile_df) == 0:
            raise ValueError('Unknown profile: ' + _profile)
        return ABMParameters(ps, camp, profile_df, override_dct)
    elif _model == NetworkModel.ID:
        override_dct = {} if overrides is None else json.loads(overrides)
        profile_df = ps.get_params(_model, _profile) if (
                type(_profile) is str) else _profile
        if len(profile_df) == 0:
            raise ValueError('Unknown profile: ' + _profile)
        return NMParameters(ps, camp, profile_df, override_dct)
    else:
        raise RuntimeError('Unsupported model: '+_model)


def create_params_abm(ps, _model, _profile, camp, overrides=None):
    override_dct = {} if overrides is None else json.loads(overrides)
    profile_df = ps.get_params(_model, _profile) if (
            type(_profile) is str) else _profile
    if len(profile_df) == 0:
        raise ValueError('Unknown profile: ' + _profile)
    return ABMParameters(ps, camp, profile_df, override_dct)