
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.tools as tls

#import sqlalchemy as sa 

#import matplotlib.pyplot as plt
#import seaborn as sns

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import datetime as dt
import locale

import sys
import warnings

import flask
from flask import send_file
import io
import ast
import pickle


#===============================================================

df_sales = pd.read_parquet('data/sales.pq')
df_products = pd.read_csv('data/products.csv')
df_clients = pd.read_csv('data/clients.csv')

branch_dict = pd.read_csv('data/branch.csv', index_col=0, header=None, names=['id', 'name'])['name'].to_dict()
brand_dict = pd.read_csv('data/brand.csv', index_col=0, header=None, names=['id', 'name'])['name'].to_dict()
manager_dict = pd.read_csv('data/manager.csv', index_col=0, header=None, names=['id', 'name'])['name'].to_dict()
group_dict = pd.read_csv('data/group.csv', index_col=0, header=None, names=['id', 'name'])['name'].to_dict()
channel_dict = pd.read_csv('data/channel.csv', index_col=0, header=None, names=['id', 'name'])['name'].to_dict()
mark_dict = pd.read_csv('data/mark.csv', index_col=0, header=None, names=['id', 'name'])['name'].to_dict()

df_clients.set_index('ID_client', inplace=True)
df_products.drop(columns='Unnamed: 0', inplace=True)

df_sales['id_brand'] = df_sales.id_commodity.map(dict(zip(df_products.ID_product, df_products.Brand_id)))
df_sales['id_group'] = df_sales.id_commodity.map(dict(zip(df_products.ID_product, df_products.Brand_id)))
df_sales['id_manager'] = df_sales.id_commodity.map(dict(zip(df_products.ID_product, df_products.Manager_id)))
df_sales['id_mark'] = df_sales.id_commodity.map(dict(zip(df_products.ID_product, df_products.Mark_id)))
df_sales['id_channel'] = df_sales.id_client.map(dict(zip(df_clients.index, df_clients.Channel_id)))
df_sales['id_branch'] = df_sales.id_client.map(dict(zip(df_clients.index, df_clients.id_branch)))

def sort_dict(a):
    kk = [(key, value) for (key, value) in sorted(a.items(), key=lambda x: x[1])]
    my_dict_branch = {}
    for i in kk:
        my_dict_branch[i[0]] = i[1]    
    return my_dict_branch

branch_dict = sort_dict(branch_dict)


# default time periods: fact period minus 3 months, base period - 3 months before fact

months_backward = 6
dt_base_start = (datetime.now() - relativedelta(months=months_backward))#.strftime('%Y-%m-01')
dt_base_end = (dt_base_start + relativedelta(months=3))
y1 = pd.to_datetime(datetime.now()).year
m1 = pd.to_datetime(datetime.now()).month
cur_m_first_day = pd.Timestamp(y1, m1, 1)

dt_base_start = cur_m_first_day - relativedelta(months=months_backward)
dt_base_end = dt_base_start + relativedelta(months=3)

dt_fact_start = cur_m_first_day - relativedelta(months=3)
dt_fact_end = cur_m_first_day

date_base_start = dt_base_start
date_base_end = dt_base_end - relativedelta(days=1)
date_fact_start = dt_fact_start
date_fact_end = dt_fact_end - relativedelta(days=1)


# Dropbox dictionaries

brand_list_dic = [{'label': value, 'value': key} for key, value in brand_dict.items()]
dept_list_dic = [{'label': value, 'value': key} for key, value in branch_dict.items()]
manager_list_dic = [{'label': value, 'value': key} for key, value in manager_dict.items()]
group_list_dic = [{'label': value, 'value': key} for key, value in group_dict.items()]
channel_list_dic = [{'label': value, 'value': key} for key, value in channel_dict.items()]
mark_list_dic = [{'label': value, 'value': key} for key, value in mark_dict.items()]


#================================================================================================
external_scripts = ['js/bootstrap.min.js']
external_stylesheets = ['css/bootstrap.min.css'] # это необходимо для правильного отображения DBC
app = dash.Dash(__name__, external_scripts=external_scripts, external_stylesheets=external_stylesheets)

app = dash.Dash()

app.layout = html.Div([

    html.H3('Factorial Analysis of Profit', style={'color':'#518cc8', 'marginBottom':30, 'marginLeft':10}),

    

    html.P('Select base and fact periods', style={'marginBottom':1, 'marginLeft':10, 'color':'#518cc8'}),

    dbc.Row([        
        dbc.Col(
            

            dcc.DatePickerRange(
                id='base_period',
                start_date=date_base_start,
                end_date=date_base_end,
                start_date_placeholder_text='DD.MM.YYYY',
                end_date_placeholder_text='(select date)',
                display_format='DD.MM.YYYY',
            ), style={'marginLeft': 10}
        ),

    
        dbc.Col(
            
            dcc.DatePickerRange(
                id='fact_period',
                start_date=date_fact_start,
                end_date=date_fact_end,
                start_date_placeholder_text='DD.MM.YYYY',
                end_date_placeholder_text='(select date)',
                display_format='DD.MM.YYYY',
            ),  style={'marginLeft': 10}
        ) 

        ]),

    
    
    html.Div(style={'padding': 2}),   
        
        #=============================================
        #AXES
        
        dbc.Row([
        
        dbc.Col(
                html.Div(["what's on the Y axis?",
                    dcc.Dropdown(
                        id='y_axis',
                        options=[
                            {'label': 'Branch', 'value': 'branch'},
                            {'label': 'Channel', 'value': 'Channel'},
                            {'label': 'Brand', 'value': 'Brand'},
                            {'label': 'Group', 'value': 'Product_group'},
                            {'label': 'Mark', 'value': 'Mark'},
                            {'label': 'Manager', 'value': 'Manager_Marketing'}


                        ],
                        value='branch',                        
                        
                    )],

                ),style={'color':'#518cc8', 'display': 'inline-block'},
            ), 

        dbc.Col(
                html.Div(["what's on the X axis?",
                    dcc.Dropdown(
                        id='x_axis',
                        options=[
                            {'label': 'Branch', 'value': 'branch'},
                            {'label': 'Channel', 'value': 'Channel'},
                            {'label': 'Brand', 'value': 'Brand'},
                            {'label': 'Group', 'value': 'Product_group'},
                            {'label': 'Mark', 'value': 'Mark'},
                            {'label': 'Manager', 'value': 'Manager_Marketing'}

                        ],
                        value='Brand',
                        #style=dict(verticalAlign="middle")#width='60%', 
                    )],                    
                     
                ),style={'color':'#518cc8', 'display': 'inline-block',"margin-left": "15px"},  #'marginLeft':2, 
            ),
     
        #=========================================
        # FILTERS


        dbc.Col(
                html.Div(['Branch filter',
                    dcc.Dropdown(
                        id='my_dropdown_dept2',
                        options = dept_list_dic,
                        multi = True,                        
                        placeholder='All branches',
                        style={'font-size': '90%', 'white-space':'nowrap', 'overflow': 'visible'}
                        
                        
                    )], style={"width": "150%"},                     
                     
                ), style={'color':'#518cc8', 'display': 'inline-block',"margin-left": "50px"}#, width=1#, 'marginLeft':2, 
            ),


        dbc.Col(
                html.Div(['Channel filter',
                    dcc.Dropdown(
                        id='my_dropdown_channel',
                        options= channel_list_dic,
                        multi = True,
                        placeholder='All channels',
                        style={'font-size': '90%', 'white-space':'nowrap', 'overflow': 'visible' }
                        #style=dict(verticalAlign="middle")#width='60%', 
                    )], style={"width": "150%"},                     
                     
                ), style={'color':'#518cc8', 'display': 'inline-block',"margin-left": "50px"}#, width=1,
            ), 




        dbc.Col(
            html.Div(['Brand filter',
                dcc.Dropdown(
                    id='my_dropdown_brand2',
                    options= brand_list_dic,
                    multi = True,
                    placeholder='All brands',
                    style={'font-size': '90%', 'white-space':'nowrap', 'overflow': 'visible' }
                    #style=dict(verticalAlign="middle")#width='60%', 
                )], style={"width": "150%"},                      
                    
            ), style={'color':'#518cc8', 'display': 'inline-block',"margin-left": "50px"}#, width=1,
        ), 




        dbc.Col(
            html.Div(['Manager filter',
                dcc.Dropdown(
                    id='my_dropdown_manager2',
                    placeholder='All managers',
                    options= manager_list_dic,
                    multi = True,
                    style={'font-size': '90%', 'white-space':'nowrap', 'overflow': 'visible' }
                     
                )], style={"width": "150%"},                     
                    
            ), style={'color':'#518cc8', 'display': 'inline-block',"margin-left": "50px"}#, width=1,
        ),


        dbc.Col(
                html.Div(['Group filter',
                    dcc.Dropdown(
                        id='my_dropdown_group',
                        options = group_list_dic,
                        multi = True,
                        #value=[],
                        placeholder='All groups',
                        style={'font-size': '90%', 'white-space':'nowrap', 'overflow': 'visible' }
                        
                    )], style={"width": "150%"},                     
                     
                ), style={'color':'#518cc8', 'display': 'inline-block',"margin-left": "50px"}#, width=1, 
            ),


            dbc.Col(
                html.Div(['Mark filter    ',
                    dcc.Dropdown(
                        id='my_dropdown_mark',
                        options = mark_list_dic,
                        multi = True,
                        #value=['Волгоград'],
                        placeholder='All marks',
                        style={'font-size': '90%', 'white-space':'nowrap', 'overflow': 'visible' } #'overflow': 'scroll'
                        #style={'font-size': '90%', 'verticalAlign':"super"},
                        
                    )], style={"width": "150%"},                    
                     
                ), style={'color':'#518cc8', 'display': 'inline-block',"margin-left": "50px"}, 
            ),   


        ]),

    
    html.Div(id='output1'),

    # EXPORT
    
    html.P('EXPORT DETAILED INFORMATION TO EXCEL', style={'marginBottom':12, 'marginLeft':10, 'color':'#518cc8'}),


    html.Div([
            
            dcc.Dropdown(
            id='my_dropdown_brand',
            options = brand_list_dic,            
            placeholder='All brands',
            style=dict(width='45%', verticalAlign="middle", marginLeft=10),     
            multi=True             
            ),
        
        
            dcc.Dropdown(
            id='my_dropdown_dept',
            options = dept_list_dic,            
            placeholder='All branches',            
            style=dict(width='45%', verticalAlign="middle", marginLeft=10),     
            multi=True),


            dcc.Dropdown(
            id='my_dropdown_manager',
            options = manager_list_dic,
            placeholder='All managers',            
            style=dict(width='45%', verticalAlign="middle", marginLeft=10),     
            multi=True),



            dcc.Dropdown(
            id='my_dropdown_channel2',
            options = channel_list_dic,
            placeholder='All channels',            
            style=dict(width='45%', verticalAlign="middle", marginLeft=10),     
            multi=True),
                        
                            
            html.H2(''),
            html.A('Click here to export', id='output2', style={'marginLeft':10})

        ]),

    
])


@app.callback(
    Output(component_id='output1', component_property='children'),
   
    [Input ('base_period', 'start_date'),
     Input ('base_period', 'end_date'),
     Input ('fact_period', 'start_date'),
     Input ('fact_period', 'end_date'),
     Input ('y_axis', 'value'),
     Input ('x_axis', 'value'),
     Input ('my_dropdown_dept2', 'value'),
     Input ('my_dropdown_channel', 'value'),
     Input ('my_dropdown_brand2', 'value'),
     Input ('my_dropdown_manager2', 'value'),
     Input ('my_dropdown_group', 'value'),     
     Input ('my_dropdown_mark', 'value')
    ])

def calc_factor(date_base_start, date_base_end, date_fact_start, date_fact_end, y_axis, x_axis, my_dept, my_channel, my_brand, my_manager, my_group, my_mark):


    print('Отдел:', my_dept)
    print('Бренд:', my_brand)
    print('Менеджер:', my_manager)
    print('Группа1:', my_group)    
    print('Метка:', my_mark)
    print('Что по оси Х:', x_axis)
    print('Что по оси У:', y_axis)


    my_dept = list(branch_dict.keys()) if not my_dept else my_dept if type(my_dept)==list else [my_dept]
    my_brand = list(brand_dict.keys()) if not my_brand else my_brand if type(my_brand)==list else [my_brand]
    my_channel = list(channel_dict.keys()) if not my_channel else my_channel if type(my_channel)==list else [my_channel]
    my_manager = list(manager_dict.keys()) if not my_manager else my_manager if type(my_manager)==list else [my_manager]
    my_group = list(group_dict.keys()) if not my_group else my_group if type(my_group)==list else [my_group]
    my_mark = list(mark_dict.keys()) if not my_mark else my_mark if type(my_mark)==list else [my_mark]
     
    

    #==================================================================================
    

    # Periods    

    y1 = pd.to_datetime(date_base_end).year
    m1 = pd.to_datetime(date_base_end).month
    d1 = pd.to_datetime(date_base_end).day
    h1 = 23
    min1 = 59
    s1 = 59

    date_base_end_convert = pd.Timestamp(y1, m1, d1, h1, min1, s1)

    y1 = pd.to_datetime(date_fact_end).year
    m1 = pd.to_datetime(date_fact_end).month
    d1 = pd.to_datetime(date_fact_end).day
    h1 = 23
    min1 = 59
    s1 = 59

    date_fact_end_convert = pd.Timestamp(y1, m1, d1, h1, min1, s1)

    my_cols = df_products.columns
    my_cl_cols = df_clients.columns


    # creating dataframes for base and fact periods     
    
    d_b = df_sales.loc[(df_sales.DocumentDate >= date_base_start) & (df_sales.DocumentDate <= date_base_end_convert)  \
          & (df_sales.id_branch.isin(my_dept)) & (df_sales.id_channel.isin(my_channel)) & (df_sales.id_brand.isin(my_brand)) & (df_sales.id_manager.isin(my_manager)) & \
          (df_sales.id_group.isin(my_group)) & (df_sales.id_mark.isin(my_mark))].groupby(['id_commodity', 'id_client']).agg({'SalesAmount': 'sum', 'SalesCost': 'sum',\
                                                                                            'SalesQty': 'sum', 'id_branch': 'max'}).reset_index().copy(deep=True)

    d_f = df_sales.loc[(df_sales.DocumentDate >= date_fact_start) & (df_sales.DocumentDate <= date_fact_end_convert)  & \
        (df_sales.id_branch.isin(my_dept)) & (df_sales.id_channel.isin(my_channel)) & (df_sales.id_brand.isin(my_brand)) & (df_sales.id_manager.isin(my_manager)) & \
        (df_sales.id_group.isin(my_group)) & (df_sales.id_mark.isin(my_mark))].groupby(['id_commodity', 'id_client']).agg({'SalesAmount': 'sum', 'SalesCost': 'sum',\
                                                                                            'SalesQty': 'sum', 'id_branch': 'max'}).reset_index().copy(deep=True)

    
    
    dm = pd.merge(d_b, d_f, left_on=['id_commodity', 'id_client'], right_on=['id_commodity', 'id_client'], how='outer', suffixes=('_base', '_fact'))  
    dm['comm_cl'] = dm.id_commodity.astype(str) + dm.id_client.astype(str)
    dm['id_department'] = dm.id_branch_base
    dm.loc[dm.id_department.isnull() == True, 'id_department'] = dm.id_branch_fact

    # adding fact and base price and cost 
    dm['price_base'] = dm.SalesAmount_base/dm.SalesQty_base
    dm['price_fact'] = dm.SalesAmount_fact/dm.SalesQty_fact
    dm['cost_base'] = dm.SalesCost_base/dm.SalesQty_base
    dm['cost_fact'] = dm.SalesCost_fact/dm.SalesQty_fact

    dm.replace([np.inf, -np.inf], np.nan, inplace=True)
    dm.fillna(0, inplace=True)

    # adding base and fact profit and profitability
    dm['pr_base'] = dm.SalesAmount_base - dm.SalesCost_base
    dm['pr_fact'] = dm.SalesAmount_fact - dm.SalesCost_fact
    dm['rent_base'] = dm.pr_base / dm.SalesCost_base
    dm['rent_fact'] = dm.pr_fact / dm.SalesCost_fact

    dm.reset_index(inplace=True)
    order_col = ['id_commodity', 'id_client', 'comm_cl', 'id_department', 'SalesAmount_base', 'SalesCost_base', 'SalesQty_base', 'pr_base', 'rent_base', 'SalesAmount_fact', 'SalesCost_fact', 'SalesQty_fact', 'pr_fact', 'rent_fact',\
                'price_base', 'price_fact', 'cost_base', 'cost_fact']
    dm =dm[order_col]

    # factorial analysis logic: changes due to price, cost, volume (structure)
    dm['is_absent'] = (dm.SalesQty_base == 0) + (dm.SalesQty_fact == 0) + (dm.SalesCost_base < 0) + (dm.SalesCost_fact < 0)
    dm['delta_price'] = np.where(dm.is_absent > 0, 0, (dm.price_fact - dm.price_base) * dm.SalesQty_fact)
    dm['delta_cost'] = np.where(dm.is_absent > 0, 0, (dm.cost_base - dm.cost_fact) * dm.SalesQty_fact)
    dm['delta_vol'] = np.where(dm.is_absent > 0, dm.pr_fact - dm.pr_base, (dm.SalesQty_fact - dm.SalesQty_base) * (dm.price_base - dm.cost_base))


    # adding reference cols
    my_cols_eng = ['ID_product', 'Article', 'Brand', 'Product_group', 'Mark', 'Manager_Marketing', 'Manager_Supply', 'ABC_XYZ']
    my_cl_cols_eng = ['id_branch', 'Channel', 'Client_name']

    dm1 = df_products[my_cols_eng].set_index('ID_product').join(dm.set_index('id_commodity'), how='right').reset_index().set_index('id_client').join(df_clients[my_cl_cols_eng]).reset_index()
    dm1.rename(columns = {'level_0': 'id_client', 'index':'id_commodity'}, inplace=True)

    dm1['branch'] = dm1.id_branch.map(branch_dict)

    cols_order = [

    'branch',
    'comm_cl',
    'id_commodity',
    'id_client',
    'id_department',
    'Article',
    'Brand',
    'Product_group',
    'Mark',
    'Manager_Marketing',
    'Manager_Supply',    
    'ABC_XYZ',
    'Client_name',
    'Channel',
    'SalesAmount_base',
    'SalesCost_base',
    'SalesQty_base',
    'pr_base',
    'rent_base',
    'SalesAmount_fact',
    'SalesCost_fact',
    'SalesQty_fact',
    'pr_fact',
    'rent_fact',
    'price_base',
    'price_fact',
    'cost_base',
    'cost_fact',
    'is_absent',
    'delta_price',
    'delta_cost',
    'delta_vol'

    ]

    dm1 = dm1[cols_order]


    dm1.rename(columns = {'SalesAmount_base':'Revenue base',
                    'SalesCost_base': 'Cost of Sales base',
                    'SalesQty_base': 'Sales base, pcs',
                    'pr_base': 'Profit base',
                    'rent_base': 'Profitability base',
                    'SalesAmount_fact' : 'Revenue fact',
                    'SalesCost_fact': 'Cost of Sales fact',
                    'SalesQty_fact': 'Sales fact, pcs',
                    'pr_fact': 'Profit fact',
                    'rent_fact': 'Profitability fact',
                    'price_base': 'Price 1 piece base',
                    'price_fact': 'Price 1 piece fact',
                    'cost_base': 'Cost 1 piece base',
                    'cost_fact': 'Cost 1 piece fact',
                    'delta_price': 'Сhange in profit due to price',
                    'delta_cost': 'Сhange in profit due to cost',
                    'delta_vol': 'Сhange in profit due to structure',
                    'comm_cl': 'id product-client',
                    }, inplace=True)
   

    # heatmaps    
        
    a = dm1[[x_axis, 'Revenue fact']].groupby(x_axis).sum().sort_values(by='Revenue fact', ascending=False)
        
    a['abc_x_axis'] = (a['Revenue fact'] / a['Revenue fact'].sum()).cumsum()
    good_x = a.reset_index()
    good_x = good_x.iloc[:, 0]

        
    aa = dm1.groupby([x_axis, y_axis])[['Сhange in profit due to price']].sum().reset_index().sort_values('Сhange in profit due to price', ascending=False).loc[(dm1[x_axis].isin(good_x))]# & (dm1[y_axis].isin(good_y))]
    aa = aa.loc[(aa[x_axis].isin(good_x))]
    aa.dropna(inplace=True)
    pivot_price = pd.pivot_table(aa, values = 'Сhange in profit due to price', columns=x_axis, index=y_axis, aggfunc='sum' )


    bb = dm1.groupby([x_axis, y_axis])[['Сhange in profit due to cost']].sum().reset_index().sort_values('Сhange in profit due to cost', ascending=False).loc[(dm1[x_axis].isin(good_x))]# & (dm1[y_axis].isin(good_y))]
    bb = bb.loc[(bb[x_axis].isin(good_x))]
    bb.dropna(inplace=True)
    pivot_cost = pd.pivot_table(bb, values = 'Сhange in profit due to cost', columns=x_axis, index=y_axis, aggfunc='sum' )
    
    
    cc = dm1.groupby([x_axis, y_axis])[['Сhange in profit due to structure']].sum().reset_index().sort_values('Сhange in profit due to structure', ascending=False).loc[(dm1[x_axis].isin(good_x))]# & (dm1[y_axis].isin(good_y))]
    cc = cc.loc[(cc[x_axis].isin(good_x))]
    cc.dropna(inplace=True)
    pivot_vol = pd.pivot_table(cc, values = 'Сhange in profit due to structure', columns=x_axis, index=y_axis, aggfunc='sum' )
    
    angle = -60   
           
    return html.Div(children=[

        
        html.H2(' ', style={'marginTop':22}),
        
        
        html.H6('Profit of base period = ''{:,.0f}'.format(dm1['Profit base'].sum())),#, style={'background-color': '#CCE5FF'}),
        html.H6('Profit of fact period = ''{:,.0f}'.format(dm1['Profit fact'].sum())),#, style={'background-color': '#CCE5FF'}),
        html.H6('Difference = ''{:,.0f}'.format(dm1['Profit fact'].sum() - dm1['Profit base'].sum())),#, style={'background-color': '#CCE5FF'}),


        html.Div(
            dcc.Graph(id = 'heat_price',
                figure = {'data': [go.Heatmap(
            
                x = pivot_price.columns.tolist(),
                y = pivot_price.index.tolist(),
                z = pivot_price.values.tolist(),
                zmid=0,
                xgap=3,
                ygap=3,
                colorscale='RdBu'           
                
                )],

                'layout': go.Layout(                    

                    title={'text':'Price influence   ''{:,.0f}'.format(dm1['Сhange in profit due to price'].sum()), 'xanchor':'center','yanchor':'bottom', 'y':0.87},
                    titlefont=dict(size=20, color='#518cc8'),
                    xaxis=dict(showgrid=True, tickangle = angle, title = x_axis),
                    yaxis=dict(showgrid=True, categoryorder='category descending', title = y_axis),
                    font=dict(size=11),                   
                    height= 550,
                    width=620,
                    margin=dict(l=200, b=150),                    
                

               ),

             } 
        ), style={'display': 'inline-block'}  ),

        html.Div(
        
            dcc.Graph(
            id='heat_cost',
            figure = {'data': [go.Heatmap(
                
                x = pivot_cost.columns.tolist(),
                y = pivot_cost.index.tolist(),
                z = pivot_cost.values.tolist(),
                
                #hoverongaps=True,
                zmid=0,
                xgap=3,
                ygap=3,
                colorscale='RdBu'           
                
                )],

                'layout': go.Layout(
                    title={'text':'Cost influence   ''{:,.0f}'.format(dm1['Сhange in profit due to cost'].sum()), 'xanchor':'center','yanchor':'bottom', 'y':0.87},
                    titlefont=dict(size=20, color='#518cc8'),
                    xaxis=dict(showgrid=True, tickangle=angle, title = x_axis),
                    yaxis=dict(showgrid=True, categoryorder='category descending'),
                    font=dict(size=11),                   
                    height= 550,
                    width=620,
                    margin=dict(l=200, b=150)
                    
                ),

          }  

        ), style={'display': 'inline-block'}  ),

            
        html.Div(

            dcc.Graph(
            id='heat_vol',
            figure = {'data': [go.Heatmap(
                
                x = pivot_vol.columns.tolist(),
                y = pivot_vol.index.tolist(),
                z = pivot_vol.values.tolist(),
                zmid=0,
                xgap=3,
                ygap=3,
                colorscale='RdBu'           
                
                )],

                'layout': go.Layout(
                    title={'text':'Structure influence   ''{:,.0f}'.format(dm1['Сhange in profit due to structure'].sum()), 'xanchor':'center','yanchor':'bottom', 'y':0.87},
                    titlefont=dict(size=20, color='#518cc8'),
                    xaxis=dict(showgrid=True, tickangle=angle, title = x_axis),
                    yaxis=dict(showgrid=True, categoryorder='category descending'),
                    font=dict(size=11),                   
                    height= 550,
                    width=620,
                    margin=dict(l=200, b=150)
                    
                ),

          }
          
        ),  style={'display': 'inline-block'})  ,
            
        

    ])



@app.callback(
    Output(component_id='output2', component_property='href'),
   
    [Input(component_id='my_dropdown_brand', component_property='value'),
     Input(component_id='my_dropdown_dept', component_property='value'),
     Input(component_id='my_dropdown_manager', component_property='value'),
     Input(component_id='my_dropdown_channel2', component_property='value'),
     Input ('base_period', 'start_date'),
     Input ('base_period', 'end_date'),
     Input ('fact_period', 'start_date'),
     Input ('fact_period', 'end_date')
     
    ])



def update_link(my_brand, my_dept, my_manager, my_channel, date_base_start, date_base_end, date_fact_start, date_fact_end):

    my_manager_non_empty = list(manager_dict.keys()) if not my_manager else my_manager
    my_brand_non_empty = list(brand_dict.keys()) if not my_brand else my_brand
    my_dept_non_empty = list(branch_dict.keys()) if not my_dept else my_dept
    my_channel_non_empty = list(channel_dict.keys()) if not my_channel else my_channel

    return f'/dash/urlToDownload?drop1={my_brand_non_empty}&drop2={my_dept_non_empty}&drop3={my_manager_non_empty}&drop8={my_channel_non_empty}&drop4={date_base_start}&drop5={date_base_end}&drop6={date_fact_start}&drop7={date_fact_end}'


def calc_export(my_brand, my_dept, my_manager, my_channel, date_base_start, date_base_end, date_fact_start, date_fact_end):

    print(my_manager)
    print(my_dept)
    print(my_brand)



    #==================================================================================
    

    # Time Periods  

    y1 = pd.to_datetime(date_base_end).year
    m1 = pd.to_datetime(date_base_end).month
    d1 = pd.to_datetime(date_base_end).day
    h1 = 23
    min1 = 59
    s1 = 59

    date_base_end_convert = pd.Timestamp(y1, m1, d1, h1, min1, s1)

    y1 = pd.to_datetime(date_fact_end).year
    m1 = pd.to_datetime(date_fact_end).month
    d1 = pd.to_datetime(date_fact_end).day
    h1 = 23
    min1 = 59
    s1 = 59

    date_fact_end_convert = pd.Timestamp(y1, m1, d1, h1, min1, s1)

    my_cols = df_products.columns
    my_cl_cols = df_clients.columns


    d_b = df_sales.loc[(df_sales.DocumentDate >= date_base_start) & (df_sales.DocumentDate <= date_base_end_convert) & (df_sales.id_manager.isin(my_manager)) &\
                 (df_sales.id_channel.isin(my_channel)) & (df_sales.id_branch.isin(my_dept)) & (df_sales.id_brand.isin(my_brand))].groupby(['id_commodity', 'id_client']).agg({'SalesAmount': 'sum', 'SalesCost': 'sum',\
                                                                                            'SalesQty': 'sum', 'id_branch': 'max'}).reset_index().copy(deep=True)



    d_f = df_sales.loc[(df_sales.DocumentDate >= date_fact_start) & (df_sales.DocumentDate <= date_fact_end_convert) & (df_sales.id_manager.isin(my_manager)) &\
                 (df_sales.id_channel.isin(my_channel)) & (df_sales.id_branch.isin(my_dept)) & (df_sales.id_brand.isin(my_brand))].groupby(['id_commodity', 'id_client']).agg({'SalesAmount': 'sum', 'SalesCost': 'sum',\
                                                                                            'SalesQty': 'sum', 'id_branch': 'max'}).reset_index().copy(deep=True)



    # merging base and fact dataframes
    dm = pd.merge(d_b, d_f, left_on=['id_commodity', 'id_client'], right_on=['id_commodity', 'id_client'], how='outer', suffixes=('_base', '_fact'))
 
    dm['comm_cl'] = dm.id_commodity.astype(str) + dm.id_client.astype(str)
    dm['id_department'] = dm.id_branch_base
    dm.loc[dm.id_department.isnull() == True, 'id_department'] = dm.id_branch_fact

    dm['price_base'] = dm.SalesAmount_base/dm.SalesQty_base
    dm['price_fact'] = dm.SalesAmount_fact/dm.SalesQty_fact
    dm['cost_base'] = dm.SalesCost_base/dm.SalesQty_base
    dm['cost_fact'] = dm.SalesCost_fact/dm.SalesQty_fact

    dm.replace([np.inf, -np.inf], np.nan, inplace=True)
    dm.fillna(0, inplace=True)

    dm['pr_base'] = dm.SalesAmount_base - dm.SalesCost_base
    dm['pr_fact'] = dm.SalesAmount_fact - dm.SalesCost_fact
    dm['rent_base'] = dm.pr_base / dm.SalesCost_base
    dm['rent_fact'] = dm.pr_fact / dm.SalesCost_fact

    dm.reset_index(inplace=True)
    order_col = ['id_commodity', 'id_client', 'comm_cl', 'id_department', 'SalesAmount_base', 'SalesCost_base', 'SalesQty_base', 'pr_base', 'rent_base', 'SalesAmount_fact', 'SalesCost_fact', 'SalesQty_fact', 'pr_fact', 'rent_fact',\
                'price_base', 'price_fact', 'cost_base', 'cost_fact']
    dm =dm[order_col]

    # factorial analysis logic: changes due to price, cost, volume (structure)
    dm['is_absent'] = (dm.SalesQty_base == 0) + (dm.SalesQty_fact == 0) + (dm.SalesCost_base < 0) + (dm.SalesCost_fact < 0)
    dm['delta_price'] = np.where(dm.is_absent > 0, 0, (dm.price_fact - dm.price_base) * dm.SalesQty_fact)
    dm['delta_cost'] = np.where(dm.is_absent > 0, 0, (dm.cost_base - dm.cost_fact) * dm.SalesQty_fact)
    dm['delta_vol'] = np.where(dm.is_absent > 0, dm.pr_fact - dm.pr_base, (dm.SalesQty_fact - dm.SalesQty_base) * (dm.price_base - dm.cost_base))


    # reference cols
    dm1 = df_products[my_cols].set_index('ID_product').join(dm.set_index('id_commodity'), how='right').reset_index().set_index('id_client').join(df_clients[my_cl_cols]).reset_index()

    dm1.rename(columns = {'level_0': 'id_client', 'index':'id_commodity'}, inplace=True)
    dm1['branch'] = dm1.id_department.map(branch_dict)

    cols_order = [

    'branch',
    'comm_cl',
    'id_commodity',
    'id_client',
    'id_department',
    'Article',
    'Brand',
    'Product_group',
    'Mark',
    'Manager_Marketing',
    'Manager_Supply',    
    'ABC_XYZ',
    'Client_name',
    'Channel',
    'SalesAmount_base',
    'SalesCost_base',
    'SalesQty_base',
    'pr_base',
    'rent_base',
    'SalesAmount_fact',
    'SalesCost_fact',
    'SalesQty_fact',
    'pr_fact',
    'rent_fact',
    'price_base',
    'price_fact',
    'cost_base',
    'cost_fact',
    'is_absent',
    'delta_price',
    'delta_cost',
    'delta_vol'

    ]

    dm1 = dm1[cols_order]


    dm1.rename(columns = {'SalesAmount_base':'Revenue base',
                    'SalesCost_base': 'Cost of Sales base',
                    'SalesQty_base': 'Sales base, pcs',
                    'pr_base': 'Profit base',
                    'rent_base': 'Profitability base',
                    'SalesAmount_fact' : 'Revenue fact',
                    'SalesCost_fact': 'Cost of Sales fact',
                    'SalesQty_fact': 'Sales fact, pcs',
                    'pr_fact': 'Profit fact',
                    'rent_fact': 'Profitability fact',
                    'price_base': 'Price 1 piece base',
                    'price_fact': 'Price 1 piece fact',
                    'cost_base': 'Cost 1 piece base',
                    'cost_fact': 'Cost 1 piece fact',
                    'delta_price': 'Сhange in profit due to price',
                    'delta_cost': 'Сhange in profit due to cost',
                    'delta_vol': 'Сhange in profit due to structure',
                    'comm_cl': 'id product-client',
                    }, inplace=True)



    return dm1  

 #==================================================================================


@app.server.route('/dash/urlToDownload')
def download_excel():
    
    
    my_brand = flask.request.args.get('drop1')
    my_brand = ast.literal_eval(my_brand)
    
    my_dept = flask.request.args.get('drop2')
    my_dept = ast.literal_eval(my_dept)

    my_manager = flask.request.args.get('drop3')
    my_manager = ast.literal_eval(my_manager)

    my_channel = flask.request.args.get('drop8')
    my_channel = ast.literal_eval(my_channel)

    date_base_start = flask.request.args.get('drop4')
    date_base_end = flask.request.args.get('drop5')
   
    date_fact_start = flask.request.args.get('drop6')   
    date_fact_end = flask.request.args.get('drop7')
    
     
    print('Export:')
    print(f"drop1 = {my_brand}")
    print(f'drop2 = {my_dept}')
    print(f'drop3 = {my_manager}')
    print(f'drop8 = {my_channel}')
    print(f'drop4 = {date_base_start}')
    print(f'drop5 = {date_base_end}')
    print(f'drop6 = {date_fact_start}')
    print(f'drop7 = {date_fact_end}')
    

    f = calc_export(my_brand, my_dept, my_manager, my_channel, date_base_start, date_base_end, date_fact_start, date_fact_end)

        
    #Convert DF
    strIO = io.BytesIO()
    #filename = f"ф.анализ прибыли тов.-кл. ({date_base_start}_{date_base_end}) ({date_fact_start}_{date_fact_end}).xlsx"
    with pd.ExcelWriter(strIO, engine='xlsxwriter') as writer:
        
        sheet_name = 'product-client'
            
        f.to_excel(writer, sheet_name = sheet_name, startrow=0,header=True, index=True, index_label=None)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        format1 = workbook.add_format({'num_format': '#,##0.00'})
        worksheet.set_column('F:F', 15)
        worksheet.set_column('R:AI', 12, format1)
            
        worksheet.freeze_panes(1, 0)
        
        header_format1 = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#A8CED2',
        'border': 1})
        
        for col_num, value in enumerate(f.columns.values):
            worksheet.write(0, col_num + 1, value, header_format1)      
    
    strIO.seek(0)
    
    date_base_start = str(pd.to_datetime(date_base_start).strftime('%Y-%m-%d'))
    date_base_end = str(pd.to_datetime(date_base_end).strftime('%Y-%m-%d'))
    date_fact_start = str(pd.to_datetime(date_fact_start).strftime('%Y-%m-%d'))
    date_fact_end = str(pd.to_datetime(date_fact_end).strftime('%Y-%m-%d'))

    return send_file(strIO, mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     attachment_filename=f'f.profit analysis ({date_base_start}_{date_base_end}) ({date_fact_start}_{date_fact_end}).xlsx',
                     as_attachment=True,
                     cache_timeout=0)





if __name__ == '__main__':
     app.run_server(debug=False)

