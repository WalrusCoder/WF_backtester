import pickle

from dash import Input, Output, State, callback, no_update

from WF_model import *

# Handles optres row selection -> backtest
@callback(
    Output('tbl_main','data',allow_duplicate=True),
    Output('tbl_main','style_data_conditional',allow_duplicate=True),
    Output('tbl_opt_res','style_data_conditional'),
    Input('tbl_opt_res','active_cell'),
    Input('tbl_opt_res','data'),
    State('lastRowClicked','children'),    
    State('tbl_main','data'),
    State('strPickled_p_multi','children'),
    prevent_initial_call=True)
def CB_OptResRowSelected(   active_cell,
                            optres_table_data,
                            main_table_row,
                            main_table_data,
                            strPickled_p_multi):
    
    # bytes(strat_params,encoding='latin1')
    p_multi = pickle.loads(bytes(strPickled_p_multi,encoding='latin1'))

    if active_cell:
        row_index = active_cell['row'] # current incremental row - used for styling only
        selected_optres_row_id = active_cell['row_id'] # Not "row", which is sensitive to sorting
        row_dict = optres_table_data[selected_optres_row_id]

        main_table_cond_style = []

        # For each of the strategy's parameters
        for param_id in p_multi.keys():

            # Get its value in the optres table, and set it in correct place in the main table
            main_table_data[main_table_row][param_id] = row_dict[param_id]

            # Set green bg for that cell in main table
            cell_styling_dict = {
                'if': {'column_id': param_id, 'row_index': main_table_row},
                'backgroundColor': 'green'
            }
            main_table_cond_style = main_table_cond_style + [cell_styling_dict]

        # Find current row_index with "id" column = selected_optres_row_id
        # Set green background of the main table row that got optimized
        # Using filter_query to highlight the row with the correct id
        optres_table_cond_style = [
            {'if': {'filter_query': f"{{id}} = {selected_optres_row_id}"},
            'backgroundColor': 'green'}
        ]

        return main_table_data, main_table_cond_style, optres_table_cond_style

    else:
        return no_update,no_update,no_update
