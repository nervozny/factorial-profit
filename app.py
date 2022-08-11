import pandas as pd
import numpy as np
import streamlit as st
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

import datetime as dt
import locale
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import sys
import warnings

import io
import pickle

#========================= SET LAYOUTS ======================================

st.set_page_config(layout="wide")

#========================= IMPORT DATA ==============================

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

# ========================= ADD ids to dataframe =========================

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

#========================= AXES =========================

st.sidebar.markdown('---')
axes_options = {
    'Branch': 'branch', 
    'Channel': 'Channel', 
    'Brand': 'Brand', 
    'Group': 'Product_group', 
    'Mark': 'Mark', 
    'Manager': 'Manager_Marketing'
}

x_ax = st.sidebar.selectbox("➡️ what's on the X axis?", list(axes_options.keys()), 0)
y_ax = st.sidebar.selectbox("⬆️ what's on the Y axis?", list(axes_options.keys()), 2)

if x_ax == y_ax:
    st.error('The axes must have different data')
    sys.exit()

# ========================= SIDEBAR FILTERS =========================
st.sidebar.markdown('---')

m_dept = st.sidebar.multiselect("Branch", pd.Series(branch_dict) )
m_channel = st.sidebar.multiselect("Channel", pd.Series(channel_dict) )
m_brand = st.sidebar.multiselect("Brand", pd.Series(brand_dict) )
m_manager = st.sidebar.multiselect("Manager", pd.Series(manager_dict) )
m_group = st.sidebar.multiselect("Group", pd.Series(group_dict) )
m_mark = st.sidebar.multiselect("Mark", pd.Series(mark_dict) )

# convert to ids

my_channel = list(channel_dict.keys()) if not m_channel else [k for k, v in channel_dict.items() if v in m_channel]
my_dept = list(branch_dict.keys()) if not m_dept else [k for k, v in branch_dict.items() if v in m_dept]
my_brand = list(brand_dict.keys()) if not m_brand else [k for k, v in brand_dict.items() if v in m_brand]
my_manager =list(manager_dict.keys()) if not m_manager else [k for k, v in manager_dict.items() if v in m_manager]
my_group = list(group_dict.keys()) if not m_group else [k for k, v in group_dict.items() if v in m_group]
my_mark = list(mark_dict.keys()) if not m_mark else [k for k, v in mark_dict.items() if v in m_mark]

# filters for export to excel

st.sidebar.markdown('---')

m_dept_load = st.sidebar.multiselect("Branch to export", pd.Series(branch_dict), default=['Castle Rock'])
m_brand_load = st.sidebar.multiselect("Brand to export", pd.Series(brand_dict), default=['Mondobondo'] )
m_manager_load = st.sidebar.multiselect("Manager to export", pd.Series(manager_dict), default=['Pete the Scab'])

# convert to ids

my_dept_load = list(branch_dict.keys()) if not m_dept_load else [k for k, v in branch_dict.items() if v in m_dept_load]
my_brand_load = list(brand_dict.keys()) if not m_brand_load else [k for k, v in brand_dict.items() if v in m_brand_load]
my_manager_load =list(manager_dict.keys()) if not m_manager_load else [k for k, v in manager_dict.items() if v in m_manager_load]


# =============================== TIME INTERVALS =============================== 

st.markdown("# Factorial Analysis of Profit (demo) ")

left_column, right_column = st.columns([1, 3])

with left_column:

    date_base_start, date_base_end = st.date_input(label='📅 Base Interval', value=[pd.Timestamp('2020-01-01'), pd.Timestamp('2020-03-31')])
    date_fact_start, date_fact_end = st.date_input(label='📅 Fact Interval', value=[pd.Timestamp('2021-01-01'), pd.Timestamp('2021-03-31')])

date_base_start = pd.Timestamp(date_base_start)
date_fact_start = pd.Timestamp(date_fact_start)

# =============================== FACTORIAL PROFIT ANALYSIS ===============================

# adjust end dates    
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

# filtering

d_b = df_sales.loc[(df_sales.DocumentDate >= date_base_start) & (df_sales.DocumentDate <= date_base_end_convert)  \
          & (df_sales.id_branch.isin(my_dept)) & (df_sales.id_channel.isin(my_channel)) & (df_sales.id_brand.isin(my_brand)) & (df_sales.id_manager.isin(my_manager)) & \
          (df_sales.id_group.isin(my_group)) & (df_sales.id_mark.isin(my_mark))].groupby(['id_commodity', 'id_client']).agg({'SalesAmount': 'sum', 'SalesCost': 'sum',\
                                                                                            'SalesQty': 'sum', 'id_branch': 'max'}).reset_index()

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
dm = dm[order_col]

# factorial analysis logic: changes due to price, cost, volume (structure)
dm['is_absent'] = (dm.SalesQty_base == 0) + (dm.SalesQty_fact == 0) + (dm.SalesCost_base < 0) + (dm.SalesCost_fact < 0)
dm['delta_price'] = np.where(dm.is_absent > 0, 0, (dm.price_fact - dm.price_base) * dm.SalesQty_fact)
dm['delta_cost'] = np.where(dm.is_absent > 0, 0, (dm.cost_base - dm.cost_fact) * dm.SalesQty_fact)
dm['delta_vol'] = np.where(dm.is_absent > 0, dm.pr_fact - dm.pr_base, (dm.SalesQty_fact - dm.SalesQty_base) * (dm.price_base - dm.cost_base))


# adding reference cols
my_cols_eng = ['ID_product','Article', 'Brand', 'Product_group', 'Mark', 'Manager_Marketing', 'Manager_Supply', 'ABC_XYZ']
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

dm1.rename(columns = {
    'SalesAmount_base':'Revenue base',
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

# lookup axes ids
x_axis = axes_options[x_ax]
y_axis = axes_options[y_ax]

a = dm1[[x_axis, 'Revenue fact']].groupby(x_axis).sum().sort_values(by='Revenue fact', ascending=False)
a['abc_x_axis'] = (a['Revenue fact'] / a['Revenue fact'].sum()).cumsum()
good_x = a.reset_index()
good_x = good_x.iloc[:, 0]
    
aa = dm1.groupby([x_axis, y_axis])[['Сhange in profit due to price']].sum().reset_index().sort_values('Сhange in profit due to price', ascending=False)
aa.dropna(inplace=True)
pivot_price = pd.pivot_table(aa, values = 'Сhange in profit due to price', columns=x_axis, index=y_axis, aggfunc='sum' )

bb = dm1.groupby([x_axis, y_axis])[['Сhange in profit due to cost']].sum().reset_index().sort_values('Сhange in profit due to cost', ascending=False)
bb.dropna(inplace=True)
pivot_cost = pd.pivot_table(bb, values = 'Сhange in profit due to cost', columns=x_axis, index=y_axis, aggfunc='sum' )    

cc = dm1.groupby([x_axis, y_axis])[['Сhange in profit due to structure']].sum().reset_index().sort_values('Сhange in profit due to structure', ascending=False)
cc.dropna(inplace=True)
pivot_vol = pd.pivot_table(cc, values = 'Сhange in profit due to structure', columns=x_axis, index=y_axis, aggfunc='sum' )

angle = -60

# =============================== Summary Information ===============================
  
right_column.markdown(
    f"> 💰 Profit of base period = {dm1['Profit base'].sum():,.0f}\n>\n" \
    f"> 💰 Profit of fact period = {dm1['Profit fact'].sum():,.0f}\n>\n"
    f"> 💰 Difference = {dm1['Profit fact'].sum() - dm1['Profit base'].sum():,.0f}\n>\n")
    

# =============================== DRAWING ===============================
left_col, mid_col, right_col = st.columns(3)

with left_col:
    data = go.Heatmap(
                x = pivot_price.columns.tolist(),
                y = pivot_price.index.tolist(),
                z = pivot_price.values.tolist(),
                zmid=0,
                xgap=3,
                ygap=3,
                colorscale='RdBu'            
            )
    layout = go.Layout(                    
                title={'text':'Price influence   ''{:,.0f}'.format(dm1['Сhange in profit due to price'].sum()), 'xanchor':'left','yanchor':'bottom', 'y':0.87},
                titlefont=dict(size=20, color='#518cc8'),
                xaxis=dict(showgrid=False, tickangle = angle),
                yaxis=dict(showgrid=False, categoryorder='category descending'),
                font=dict(size=11),                   
                height= 550,
                width=550,
                margin=dict(l=0, b=0),                    
            )


    fig = go.Figure(data=[data], layout=layout)
    st.plotly_chart(fig, use_container_width=False)

with mid_col:
    data = go.Heatmap(
                x = pivot_cost.columns.tolist(),
                y = pivot_cost.index.tolist(),
                z = pivot_cost.values.tolist(),
                zmid=0,
                xgap=3,
                ygap=3,
                colorscale='RdBu'            
            )
    layout = go.Layout(                    
                title={'text':'Cost influence   ''{:,.0f}'.format(dm1['Сhange in profit due to cost'].sum()), 'xanchor':'left','yanchor':'bottom', 'y':0.87},
                titlefont=dict(size=20, color='#518cc8'),
                xaxis=dict(showgrid=False, tickangle = angle),
                yaxis=dict(showgrid=False, categoryorder='category descending'),
                font=dict(size=11),                   
                height= 550,
                width=550,
                margin=dict(l=0, b=0),                    
            )
    fig = go.Figure(data=[data], layout=layout)
    st.plotly_chart(fig, use_container_width=False)

with right_col:
    data = go.Heatmap(
                x = pivot_vol.columns.tolist(),
                y = pivot_vol.index.tolist(),
                z = pivot_vol.values.tolist(),
                zmid=0,
                xgap=3,
                ygap=3,
                colorscale='RdBu'            
            )
    layout = go.Layout(                    
                title={'text':'Structure influence   ''{:,.0f}'.format(dm1['Сhange in profit due to structure'].sum()), 'xanchor':'left','yanchor':'bottom', 'y':0.87},
                titlefont=dict(size=20, color='#518cc8'),
                xaxis=dict(showgrid=False, tickangle = angle),
                yaxis=dict(showgrid=False, categoryorder='category descending'),
                font=dict(size=11),                   
                height= 550,
                width=550,
                margin=dict(l=0, b=0),                    
            )
    fig = go.Figure(data=[data], layout=layout)
    st.plotly_chart(fig, use_container_width=False)



# =============================== EXPORT TO EXCEL ===============================

manager_load_list = [v for k, v in manager_dict.items() if k in my_manager_load]
brand_load_list = [v for k, v in brand_dict.items() if k in my_brand_load]

dm1_exp = dm1.loc[(dm1.id_department.isin(my_dept_load)) & (dm1.Brand.isin(brand_load_list)) & (dm1.Manager_Marketing.isin(manager_load_list))].copy()

@st.experimental_memo
def calc_export():
    strIO = io.BytesIO()
    with pd.ExcelWriter(strIO, engine='xlsxwriter') as writer:
        sheet_name = 'product-client'
        dm1_exp.to_excel(writer, sheet_name = sheet_name, startrow=0, header=True, index=True, index_label=None)
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
        
        for col_num, value in enumerate(dm1_exp.columns.values):
            worksheet.write(0, col_num + 1, value, header_format1)      
    
    strIO.seek(0)
    return strIO

st.sidebar.download_button( label="💾 Export to excel", 
                            data=calc_export(),
                            file_name='profit_analysis.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        )
st.sidebar.markdown('---')

