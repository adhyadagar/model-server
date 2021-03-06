import textwrap
import dash_html_components as html
import dash_core_components as dcc
from ai4good.webapp.apps import dash_app, facade, model_runner, cache, local_cache, cache_timeout
from plotly.subplots import make_subplots
from ai4good.webapp.model_results_config import model_profile_config
from collections import defaultdict
from ai4good.webapp.model_results_utils import load_report
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
# this needs to be changed later
from ai4good.models.cm.initialise_parameters import Parameters
import plotly.graph_objs as go
from ai4good.utils.logger_util import get_logger
from plotly.colors import DEFAULT_PLOTLY_COLORS
import ai4good.webapp.common_elements as common_elements
import pickle
import ai4good.utils.path_utils as pu


logger = get_logger(__name__)

# @cache.memoize(timeout=cache_timeout)
def layout(camp):
    # get results here based on the camp
    return html.Div(
        [
            # Hidden div inside the app that stores the intermediate value
            html.Div(camp, id='camp-name', style={'display': 'none'}),
            common_elements.nav_bar(),
            html.Div([
                html.A(html.Button('Print', className="btn btn-light"), href='javascript:window.print()', className='d-print-none', style={"float": 'right'}),
                dcc.Markdown(disclaimer(), style={'margin': 30}),
                html.H1(f'AI for Good Simulator: Model Results Dashboard for the {camp} Camp', style={
                        'margin': 30}),
                dcc.Loading(html.Div([], id='message_1_section', style={'margin': 30})),
                dcc.Markdown(high_level_message_2(), style={'margin': 30}),
                dcc.Markdown(high_level_message_3(), style={'margin': 30}),
                dcc.Markdown(high_level_message_4(), style={'margin': 30}),
                dcc.Loading(html.Div([], id='message_5_section', style={'margin': 30})),
            ], style={'margin': 30})
        ]
    )


def disclaimer():
    return textwrap.dedent('''
    ##### Disclaimer: The model results are produced based on the parameters being inputted and contain abstractions of the reality. The exact values from the model predictions are not validated by real data from your refugee camp but the rough values and ranges of reduction with relevent intervention methods are explored to provide value in planning efforts.
    ''').replace('\n', ' ')


def high_level_message_1():
    return textwrap.dedent(f'''
    ## 1. The case for a longer, more sustainable program
    As shown by comparing implementing different interventions for 1 month, 3 month and 6 month during the period of epidemic,
    it is important to prioritize long-term non-pharmaceutical intervention over short-term interventions. 
    ''')


def high_level_message_2():
    return textwrap.dedent(f'''
    ## 2. Switch on invervention like lockdown at the right time
    It is also important to switch on interventions at the correct time, rather than having them on all the time.
    This is shown by comparing implementing different interventions starting at different points during the epidemic. 
    ''')


def high_level_message_3():
    return textwrap.dedent(f'''
    ## 3. Reducing activities happening within the camp might not be that effective
    Reducing activities for the residents might not be an effective intervention. A camp lockdown is comparatively more effective 
    but must not be implemented the whole time as people will start becoming more relaxed. 
    ''')


def high_level_message_4():
    return textwrap.dedent(f'''
    ## 4. Isolating the symptomatic might not be that effective
    Isolating the symptomatically infected residents can be effective, but it is resource intensive and there is uncertainty about the final outcome. 
    ''')


def high_level_message_5():
    return textwrap.dedent(f'''
    ## 5. Characteristics of non-pharmaceutical interventions that apply to your camp
    Each non-pharmaceutical intervention has its different characteristics. It is important to implement a combinatorial approach, 
    where using several less-effective policies laid over each other prove to be more effective than using any single intervention on its own. 
    ''')


@local_cache.memoize(timeout=cache_timeout)
def load_user_results(camp):
    logger.info(f"Reading user results for camp {camp}")
    p = pu.user_results_path(f"{camp}_results_collage.pkl")
    with open(p, 'rb') as handle:
        user_results = pickle.load(handle)
        return user_results


@local_cache.memoize(timeout=cache_timeout)
def get_model_result_message(message_key, camp):
    user_results = load_user_results(camp)
    logger.info(f"Reading data for high level message: {message_key}")
    model_profile_report_dict = defaultdict(dict)
    for model in model_profile_config[message_key].keys():
        if len(model_profile_config[message_key][model]) > 0:
            for profile in model_profile_config[message_key][model]:
                model_profile_report_dict[model][profile] = user_results[model][profile]
    return model_profile_report_dict


# @local_cache.memoize(timeout=cache_timeout)
# def get_model_result(camp: str, profile: str):
#     logging.info("Reading data for: " + camp + ", " + profile)
#     mr = model_runner.get_result(CompartmentalModel.ID, profile, camp)
#     assert mr is not None
#     profile_df = facade.ps.get_params(
#         CompartmentalModel.ID, profile).drop(columns=['Profile'])
#     params = Parameters(facade.ps, camp, profile_df, {})
#     report = load_report(mr, params)
#     return mr, profile_df, params, report

color_scheme_updated = DEFAULT_PLOTLY_COLORS


def render_message_1_plots(camp, category="Infected (symptomatic)"):
    model_profile_report_dict = get_model_result_message("message_1", camp)
    columns_to_plot = [category]
    fig = go.Figure()
    col = columns_to_plot[0]
    plot_num = 0
    for profile in model_profile_report_dict["compartmental-model"].keys():
        if profile == 'baseline':
            label_name = 'No interventions'
            hover_text = '0 month'
        elif profile == 'better_hygiene_one_month':
            label_name = 'Wearing facemask for 1 month'
            hover_text = '1 month'
        elif profile == 'better_hygiene_three_month':
            label_name = 'Wearing facemask for 3 month '
            hover_text = '3 months'
        elif profile == 'better_hygiene_six_month':
            label_name = 'Using Hand Sanitizers & facemask for 6 month'
            hover_text = '6 months'
        else:
            label_name = 'default'
            hover_text = None
        ci, line = plot_iqr(model_profile_report_dict["compartmental-model"][profile], col, label_name, hover_text)
        fig.add_trace(ci)
        fig.add_trace(line)
        fig.update_yaxes(title_text=col)
        if plot_num < len(color_scheme_updated):
            fig["data"][2 * plot_num]["line"]["color"] = color_scheme_updated[plot_num] #IQR Color
            fig["data"][2 * plot_num]["opacity"] = 0.2 #IQR Opacity
            fig["data"][2 * plot_num + 1]["line"]["color"] = color_scheme_updated[plot_num] #Curve Colour
        plot_num += 1
    x_title = 'Number of days since the virus was introduced to the camp'
    fig.update_xaxes(title_text=x_title)
    fig.update_traces(line=dict(width=2))
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=400,
        showlegend=True,
        hovermode="x"
    )
    # Match the background colour from external css style sheet
    fig.layout.paper_bgcolor = '#ecf0f1'
    fig.layout.xaxis.showspikes = True
    fig.layout.xaxis.spikemode = 'across'
    fig.layout.xaxis.spikesnap = 'cursor'
    fig.layout.xaxis.showline = True
    fig.layout.xaxis.showgrid = True

    return fig


@dash_app.callback(
    Output("plot_message1_fig", "figure"),
    [Input("camp-name", "children"), Input("message_1_selection", "value")]
)
def update_message_1_plots(camp, category):
    fig = render_message_1_plots(camp, category)
    return fig


@dash_app.callback(
    Output('message_1_section', 'children'),
    [Input("camp-name", "children")]
)
def message_1_section(camp):
    # categories of interest for plotting
    dropdown_options = [
        {"label": "Number of Symptomatically infected individuals", "value": "Infected (symptomatic)",
         "title": "Symptomatic infection includes both mild and severe cases"},
        {"label": "Number of people count per hospitalisation day", "value": "Hospitalised",
         "title": "Hospitalisation demand on a daily basis interpreted as number of people needing hospitalisation "
                  "care on that day (they might not get it)"},
        {"label": "Number of people count per critical condition day", "value": "Critical",
         "title": "Critical care demand on a daily basis interpreted as number of people needing critical care on that "
                  "day (they might not get it)"},
        {"label": "Cumulative number of deaths", "value": "Deaths", "title": "Number of cumulative deaths throughout "
                                                                             "the course of the pandemic"},
    ]
    dropdown_button = html.Div(
        [
            html.H5("Categories to inspect: "),
            dcc.Dropdown(
                id="message_1_selection",
                options=dropdown_options,
                value="Infected (symptomatic)",
                searchable=False,
                clearable=False,
                style={"width": "100%"}
            )
        ],
        style={"width": "100%"},
        className='d-print-none'
    )
    fig = render_message_1_plots(camp)
    return[
        dcc.Markdown(high_level_message_1()),
        dropdown_button,
        dcc.Graph(
            id='plot_message1_fig',
            figure=fig,
            style={'width': '100%'}
        ),
    ]


def render_message_5_plots(camp, category="Deaths"):
    model_profile_report_dict = get_model_result_message("message_5", camp)
    columns_to_plot = [category]
    fig = go.Figure()
    col = columns_to_plot[0]
    plot_num = 0
    for profile in model_profile_report_dict["compartmental-model"].keys():
        if profile == 'only_better_hygiene':
            label_name = 'Only improve personal hygiene'
            hover_text = "hygiene"
        elif profile == 'only_remove_symptomatic':
            label_name = 'Only isolate symptomatic individuals with COVID infections'
            hover_text = "isolation"
        elif profile == 'only_remove_high_risk':
            label_name = 'Only move residents who are at high risk of COVID infection offsite'
            hover_text = "removal"
        elif profile == 'combined_hygiene_symptomatic_high_risk':
            label_name = 'Combine all of the NPIs above'
            hover_text = "all"
        else:
            label_name = 'default'
            hover_text = None

        p1, p2 = plot_iqr(model_profile_report_dict["compartmental-model"][profile], col, label_name, hover_text)
        fig.add_trace(p1)
        fig.add_trace(p2)
        fig.update_yaxes(title_text=col)
        if plot_num < len(color_scheme_updated):
            fig["data"][2 * plot_num]["line"]["color"] = color_scheme_updated[plot_num] #IQR Color
            fig["data"][2 * plot_num]["opacity"] = 0.2 #IQR Opacity
            fig["data"][2 * plot_num + 1]["line"]["color"] = color_scheme_updated[plot_num] #Curve Colour
        plot_num += 1
        
    x_title = 'Number of days since the virus was introduced to the camp'
    fig.update_xaxes(title_text=x_title)
    fig.update_traces(line=dict(width=2))
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=400,
        showlegend=True,
        hovermode = "x",
    )

    # Match the background colour from external css style sheet
    fig.layout.paper_bgcolor = '#ecf0f1'
    fig.layout.xaxis.showspikes = True
    fig.layout.xaxis.spikemode = 'across'
    fig.layout.xaxis.spikesnap = 'cursor'
    fig.layout.xaxis.showline = True
    fig.layout.xaxis.showgrid = True

    return fig


@dash_app.callback(
    Output("plot_message5_fig", "figure"),
    [Input("camp-name", "children"), Input("message_5_selection", "value")]
)
def update_message_5_plots(camp, category):
    fig = render_message_5_plots(camp, category)
    return fig


@dash_app.callback(
    Output('message_5_section', 'children'),
    [Input("camp-name", "children")]
)
def message_5_section(camp):
    # categories of interest for plotting
    dropdown_options = [
        {"label": "Number of Symptomatically infected individuals", "value": "Infected (symptomatic)",
         "title": "Symptomatic infection includes both mild and severe cases"},
        {"label": "Number of people count per hospitalisation day", "value": "Hospitalised",
         "title": "Hospitalisation demand on a daily basis interpreted as number of people needing hospitalisation "
                  "care on that day (they might not get it)"},
        {"label": "Number of people count per critical condition day", "value": "Critical",
         "title": "Critical care demand on a daily basis interpreted as number of people needing critical care on that "
                  "day (they might not get it)"},
        {"label": "Cumulative number of deaths", "value": "Deaths", "title": "Number of cumulative deaths throughout "
                                                                             "the course of the pandemic"},
    ]
    dropdown_button = html.Div(
        [
            html.H5("Categories to inspect: "),
            dcc.Dropdown(
                id="message_5_selection",
                options=dropdown_options,
                value="Deaths",
                searchable=False,
                clearable=False,
                style={"width": "100%"}
            )
        ],
        style={"width": "100%"},
        className='d-print-none'
    )
    fig = render_message_5_plots(camp)
    return[
        dcc.Markdown(high_level_message_5()),
        dropdown_button,
        dcc.Graph(
            id='plot_message5_fig',
            figure=fig,
            style={'width': '100%'}
        ),
    ]



def plot_iqr(df: pd.DataFrame, y_col: str, graph_label: str, hover_text: str,
             x_col='Time', estimator=np.median,
             iqr_low=0.25, iqr_high=0.75):
    grouped = df.groupby(x_col)[y_col]
    est = grouped.agg(estimator)
    cis = pd.DataFrame(np.c_[grouped.quantile(iqr_low), grouped.quantile(iqr_high)], index=est.index,
                       columns=["low", "high"]).stack().reset_index()

    x = est.index.values.tolist()
    x_rev = x[::-1]

    y_upper = cis[cis['level_1'] == 'high'][0].values.tolist()
    y_lower = cis[cis['level_1'] == 'low'][0].values.tolist()
    y_lower = y_lower[::-1]
    
    ci = go.Scatter(
        x=x + x_rev, y=y_upper + y_lower, fill='toself', showlegend=False, hoverinfo="skip", legendgroup=f"{graph_label}")
    line = go.Scatter(x=x, y=est,  name=f'{graph_label}', line=dict(width=6), legendgroup=f"{graph_label}", 
                      text=[f'{round(number)}' for number in est],
                      hovertemplate='%{text}' + f'<extra>{hover_text}</extra>')
    return ci, line

# @dash_app.callback(
#     Output('cmp_section', 'children'),
#     [Input('_camp_param', 'children'), Input('_profile_param', 'children'), Input('_cmp_profiles', 'children')],
# )
# @cache.memoize(timeout=cache_timeout)
# def interventions(camp, profile, cmp_profiles):

#     _, base_profile, base_params, base_df = get_model_result(camp, profile)
#     profiles = cmp_profiles.split('¬')

#     if len(profiles) == 0 or (len(profiles) == 1 and len(profiles[0].strip()) == 0):
#         return []

#     intervention_content = [intervention(camp, p, i+1, base_df, base_params, base_profile, profile) for i, p in enumerate(profiles)]
#     intervention_content = reduce(list.__add__, intervention_content)

#     return [
#         dcc.Markdown(textwrap.dedent(f'''
#         ## 2. Intervention scenarios

#         We compare each intervention scenario to baseline. Baseline charts are in blue as before, intervention charts
#         are in red.
#          ''')),
#         html.Div(intervention_content)
#     ]


# def intervention(camp, cmp_profile_name, idx, base_df, base_params, base_profile, base_profile_name):
#     _, cmp_profile, cmp_params, cmp_df = get_model_result(camp, cmp_profile_name)

#     tbl = diff_table(base_df, cmp_df, cmp_params.population)
#     profile_diff = profile_diff_tbl(base_profile, base_params, cmp_profile, cmp_params)

#     return [
#         dcc.Markdown(textwrap.dedent(f'''
#         ## 2.{idx} {cmp_profile_name} intervention comparison

#         Here we compare {cmp_profile_name} model profile with base {base_profile_name} profile explored in the main
#         section. Compared to base profile {cmp_profile_name} has following changes:
#         ''')),
#         dbc.Row([
#             dbc.Col([
#                 html.B(f'{cmp_profile_name} parameter changes compared to {base_profile_name}'),
#                 dbc.Table.from_dataframe(profile_diff, bordered=True, hover=True,  striped=True),
#             ], width=4)
#         ]),
#         dcc.Markdown(textwrap.dedent(f'''
#         #### Comparison results
#         ''')),
#         dbc.Row([
#             dbc.Col([
#                 html.B(f'{cmp_profile_name} to {base_profile_name} comparison table'),
#                 dbc.Table.from_dataframe(tbl, bordered=True, hover=True)
#             ], width=4)
#         ])
#     ] + intervention_plots(base_df, cmp_df, base_profile_name, cmp_profile_name)


# def intervention_plots(base_df, cmp_df, base_profile_name, cmp_profile_name):
#     columns_to_plot = ['Infected (symptomatic)', 'Hospitalised', 'Critical', 'Deaths']
#     fig = make_subplots(rows=2, cols=2, shared_xaxes=True,
#                         vertical_spacing=0.05,
#                         horizontal_spacing=0.05,
#                         subplot_titles=columns_to_plot)

#     for i, col in enumerate(columns_to_plot):
#         row_idx = int(i % 2 + 1)
#         col_idx = int(i / 2 + 1)

#         b1, b2 = plot_iqr(base_df, col, ci_name_prefix=f'{base_profile_name} ',
#                           estimator_name=f'{base_profile_name} median')
#         c1, c2 = plot_iqr(cmp_df, col, ci_name_prefix=f'{cmp_profile_name} ',
#                           estimator_name=f'{cmp_profile_name} median', color_scheme=color_scheme_secondary)

#         fig.add_trace(b2, row=row_idx, col=col_idx)
#         fig.add_trace(c2, row=row_idx, col=col_idx)
#         fig.add_trace(b1, row=row_idx, col=col_idx)
#         fig.add_trace(c1, row=row_idx, col=col_idx)

#         fig.update_yaxes(title_text=col, row=row_idx, col=col_idx)
#     x_title = 'Time, days'
#     fig.update_xaxes(title_text=x_title, row=2, col=1)
#     fig.update_xaxes(title_text=x_title, row=2, col=2)

#     fig.update_traces(mode='lines')
#     fig.update_layout(
#         margin=dict(l=0, r=0, t=30, b=0),
#         height=800,
#         showlegend=False
#     )

#     return [
#         dcc.Graph(
#             id='intervention_plots_fig',
#             figure=fig,
#             style={'width': '100%'}
#         )
#     ]
