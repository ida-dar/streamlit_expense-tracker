import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

import database as db

import calendar
from datetime import datetime

# VARIABLES
incomes = ['Salary', 'Blog', 'Other income']
expenses = ['Rent', 'Utilities', 'Groceries', 'Car', 'Other expenses', 'Saving']
currency = 'USD'
page_title = 'Income and Expense Tracker'
layout = 'centered'

# HEADERS
dataEntry = 'Data Entry'
dataVisual = 'Data Visualization'

# PAGE CONFIGURATION
st.set_page_config(page_title=page_title, layout=layout)
st.title(page_title)


# DATABASE CONFIGURATION
def get_all_periods():
    items = db.fetch_all_periods()
    periods = [item['key'] for item in items]
    return periods


# HIDE STREAMLIT DEFAULT STYLE
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# DROPDOWN VALUES
years = [datetime.today().year, datetime.today().year + 1]
months = list(calendar.month_name[1:])

# NAVIGATION
selected = option_menu(
    menu_title=None,
    options=[dataEntry, dataVisual],
    icons=['pencil-fill', 'bar-chart-fill'],  # https://icons.getbootstrap.com/
    orientation='horizontal',
)

# INPUT & SAVE PERIODS
if selected == dataEntry:
    st.header(f'Data entry in {currency}')
    with st.form('entry_from', clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox('Select Month', months, key='month')
        col2.selectbox('Select Year', years, key='year')

        '---'  # divider between columns and button; '---' visually separates items
        with st.expander('Income'):
            for income in incomes:
                st.number_input(f'{income}:', min_value=0, format='%i', step=5, key=income)
        with st.expander('Expenses'):
            for expense in expenses:
                st.number_input(f'{expense}:', min_value=0, format='%i', step=5, key=expense)
        with st.expander('Comment'):
            comment = st.text_area('', placeholder='Enter a comment here')

        '---'
        submitted = st.form_submit_button('Save Data')
        if submitted:
            period = str(st.session_state['year']) + '_' + str(st.session_state['month'])
            incomes = {
                income: st.session_state[income] for income in incomes
            }  # in expander the 'income' was used as a key, so it can be looped here
            expenses = {
                expense: st.session_state[expense] for expense in expenses
            }

            db.insert_period(period, incomes, expenses, comment)
            st.success('Data saved successfully')


if selected == dataVisual:
    # PLOT PERIODS
    st.header(dataVisual)
    with st.form('saved_periods'):
        period = st.selectbox('Select Period:', get_all_periods())
        submitted = st.form_submit_button('Plot Period')

        if submitted:
            period_data = db.get_period(period)

            incomes = period_data.get('incomes')
            expenses = period_data.get('expenses')
            comment = period_data.get('comment')

        # Create metrics
        total_incomes = sum(incomes.values())
        total_expenses = sum(expenses.values())
        remaining_budget = total_incomes - total_expenses

        col1, col2, col3 = st.columns(3)
        col1.metric('Total Income:', f'{total_incomes} {currency}')
        col2.metric('Total Expenses:', f'{total_expenses} {currency}')
        col3.metric('Remaining Budget:', f'{remaining_budget} {currency}')
        st.write(comment)

        # Create sankey chart
        label = list(incomes.keys()) + ['Total Income'] + list(expenses.keys())
        source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
        target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses]
        value = list(incomes.values()) + list(expenses.values())

        # Data to dict, dict to sankey chart
        link = dict(source=source, target=target, value=value, color='rgba(31, 119, 180, 0.4)')
        node = dict(label=label, pad=20, thickness=30, color='rgb(255, 127, 14)')
        data = go.Sankey(link=link, node=node)

        # Plot
        fig = go.Figure(data)
        fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))  # change the margin
        st.plotly_chart(fig, use_container_width=True)  # display the chart to fill the container_width

