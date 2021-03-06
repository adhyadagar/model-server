import os

from typeguard import typechecked
from typing import List, Dict, Any
from abc import ABC, abstractmethod
import pandas as pd
import ai4good.utils.path_utils as pu


@typechecked
class ParamStore(ABC):

    @abstractmethod
    def get_models(self) -> List[str]:
        """
        Returns list of available models
        """
        pass

    @abstractmethod
    def get_camps(self) -> List[str]:
        """
        Returns list of available camps
        """
        pass

    @abstractmethod
    def get_profiles(self, model: str) -> List[str]:
        """
        Returns list of available profiles for given model
        """
        pass

    @abstractmethod
    def get_params(self, model: str, profile: str) -> pd.DataFrame:
        """
        Given model name and profile return model specific parameters
        """
        pass

    @abstractmethod
    def store_params(self, model: str, profile: str, profile_df: pd.DataFrame):
        """
            Given model and profile name store profile params
        """
        pass

    @abstractmethod
    def store_camp_params(self, camp_params_df: pd.DataFrame):
        """
            Given model and profile name store profile params
        """
        pass

    @abstractmethod
    def get_camp_params(self, camp: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_disease_params(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_generated_disease_param_vectors(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_supported_countries(self) -> List:
        pass


@typechecked
class SimpleParamStore(ParamStore):

    def get_models(self) -> List[str]:
        return ['compartmental-model', 'compartmental-model-stochastic', 'network-model', 'agent-based-model']

    def get_profiles(self, model: str) -> List[str]:
        df = self._read_csv(model + "_profile_params.csv")
        return df['Profile'].dropna().unique().tolist()

    def get_params(self, model: str, profile: str) -> pd.DataFrame:
        df = self._read_csv(model + "_profile_params.csv")
        return df[df['Profile'] == profile].copy()

    def store_params(self, model: str, profile: str, profile_df: pd.DataFrame):
        _file = model + "_profile_params.csv"
        df = self._read_csv(_file)
        df = df[df['Profile'] != profile].copy()
        profile_df['Profile'] = profile
        df = df.append(profile_df)
        df.to_csv(pu.params_path(_file), index=False)

    def store_camp_params(self, camp_params_df: pd.DataFrame):
        camp_params_df.set_index('parameter_id', inplace=True)
        _file = pu.params_subpath("camp_params", camp_params_df.loc['name-camp'].values[0] + ".csv")
        try:
            df = pd.read_csv(_file, index_col='parameter_id')
        except FileNotFoundError:
            df = pd.DataFrame()
        res = df.combine_first(camp_params_df)
        res.loc[camp_params_df.index] = camp_params_df
        res.to_csv(_file)

    def get_camps(self) -> List[str]:
        df = self._read_csv("camp_params.csv")
        return df.Camp.dropna().sort_values().unique().tolist()

    def get_camp_params(self, camp: str) -> pd.DataFrame:
        df = self._read_csv("camp_params.csv")
        return df[df.Camp == camp].copy()

    def get_camp_params_network_model(self, camp: str) -> pd.DataFrame:
        df = self._read_csv("network-model_camp_params.csv")
        return df[df.Camp == camp].copy()

    def get_disease_params(self) -> pd.DataFrame:
        return self._read_csv("disease_params.csv")

    def get_disease_params_network_model(self) -> pd.DataFrame:
        return self._read_csv("network-model_disease_params.csv")

    def get_generated_disease_param_vectors(self) -> pd.DataFrame:
        return self._read_csv("generated_params.csv")

    def get_supported_countries(self):
        countries = [f.split('.')[0] for f in os.listdir(pu.params_path('contact_matrices')) if f.endswith('.csv')]
        return countries

    @staticmethod
    def _read_csv(name: str) -> pd.DataFrame:
        return pd.read_csv(pu.params_path(name))
