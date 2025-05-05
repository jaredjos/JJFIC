import streamlit as st
import pandas as pd
import numpy as np

st.title("Jared's Financial Independence Calculator 📈")

# User Inputs
st.sidebar.header('Investment Parameters')

# Currency Selector
currency_symbol = st.sidebar.selectbox('Select Currency', ['₹', '$', '€', '£', '¥'], help='Choose your preferred currency for calculations.')

age_start = st.sidebar.number_input('Starting Age', min_value=18, max_value=100, value=30, help='Age at which you start investing.')
age_end = st.sidebar.number_input('Ending Age (Investment Stop)', min_value=age_start, max_value=100, value=45, help='Age at which you stop investing.')
age_retire = st.sidebar.number_input('Retirement Age (SWP Start)', min_value=age_end, max_value=100, value=60, help='Age at which you start systematic withdrawal plan (SWP).')

initial_lump_sum = st.sidebar.number_input(f'Initial Lump Sum ({currency_symbol})', min_value=0, value=500000, help='Initial lump sum investment.')
monthly_investment = st.sidebar.number_input(f'Initial Monthly Investment ({currency_symbol})', min_value=0, value=50000, help='Monthly investment amount.')
yearly_step_up = st.sidebar.slider('Annual Step-Up (%)', min_value=0.0, max_value=20.0, value=5.0, step=0.5, help='Annual percentage increase in monthly investment.')

annual_return = st.sidebar.slider('Annual Return (%)', min_value=1.0, max_value=50.0, value=12.0, step=0.5, help='Expected annual return percentage on investments.')
annual_inflation = st.sidebar.slider('Annual Inflation (%)', min_value=0.0, max_value=15.0, value=6.0, step=0.5, help='Annual inflation rate.')
swp_inflation = st.sidebar.slider('SWP Annual Inflation (%)', min_value=0.0, max_value=15.0, value=6.0, step=0.5, help='Annual increase rate for withdrawal amount.')

swp_monthly_withdrawal = st.sidebar.number_input(f'Monthly SWP Amount ({currency_symbol})', min_value=0, value=100000, help='Monthly withdrawal amount during retirement.')

# Custom Investments
st.sidebar.subheader('Custom Lump Sum Investments')
custom_investments = []
num_custom_investments = st.sidebar.number_input('Number of Custom Investments', min_value=0, max_value=10, value=0, help='Total number of custom lump sum investments.')

for i in range(int(num_custom_investments)):
    st.sidebar.write(f'Custom Investment {i+1}')
    year = st.sidebar.number_input(f'Year of Investment {i+1}', min_value=age_start, max_value=100, value=age_start, help='Year of custom investment.')
    month = st.sidebar.number_input(f'Month of Investment {i+1}', min_value=1, max_value=12, value=1, help='Month of custom investment.')
    amount = st.sidebar.number_input(f'Amount {i+1} ({currency_symbol})', min_value=0, value=100000, help='Amount of custom investment.')
    growth = st.sidebar.slider(f'Growth Rate {i+1} (%)', min_value=1.0, max_value=50.0, value=12.0, step=0.5, help='Growth rate of custom investment.')
    custom_investments.append((year, month, amount, growth))

# Custom Withdrawals
st.sidebar.subheader('Custom Withdrawals')
custom_withdrawals = []
num_custom_withdrawals = st.sidebar.number_input('Number of Custom Withdrawals', min_value=0, max_value=10, value=0, help='Total number of custom withdrawals.')

for i in range(int(num_custom_withdrawals)):
    st.sidebar.write(f'Custom Withdrawal {i+1}')
    year = st.sidebar.number_input(f'Year of Withdrawal {i+1}', min_value=age_retire, max_value=100, value=age_retire, help='Year of custom withdrawal.')
    month = st.sidebar.number_input(f'Month of Withdrawal {i+1}', min_value=1, max_value=12, value=1, help='Month of custom withdrawal.')
    amount = st.sidebar.number_input(f'Withdrawal Amount {i+1} ({currency_symbol})', min_value=0, value=100000, help='Amount of custom withdrawal.')
    custom_withdrawals.append((year, month, amount))

# Calculation logic
years = np.arange(age_start, 101)
df = pd.DataFrame(index=years, columns=['Age', 'Year Start Balance', 'Annual Investment', 'Custom Investments', 'Year End Balance', 'SWP Withdrawal', 'Custom Withdrawals', 'Adjusted End Balance'])
df['Age'] = years

balance = initial_lump_sum
monthly_inv = monthly_investment
current_swp = swp_monthly_withdrawal

custom_balance = {(y, m): 0 for y in years for m in range(1, 13)}
custom_withdrawal_balance = {(y, m): 0 for y in years for m in range(1, 13)}

for year, month, amount, growth in custom_investments:
    custom_balance[(year, month)] += amount

for year, month, amount in custom_withdrawals:
    custom_withdrawal_balance[(year, month)] += amount

for year in years:
    annual_investment = monthly_inv * 12 if age_start <= year < age_end else 0
    custom_investment = sum(custom_balance[(year, m)] for m in range(1, 13))
    custom_withdrawal = sum(custom_withdrawal_balance[(year, m)] for m in range(1, 13))

    balance = balance * (1 + annual_return / 100) + annual_investment + custom_investment
    df.at[year, 'Year Start Balance'] = balance - annual_investment - custom_investment
    df.at[year, 'Annual Investment'] = annual_investment
    df.at[year, 'Custom Investments'] = custom_investment
    df.at[year, 'Year End Balance'] = balance

    withdrawal = current_swp * 12 if year >= age_retire else 0
    balance -= (withdrawal + custom_withdrawal)
    if year >= age_retire:
        current_swp *= (1 + swp_inflation / 100)

    df.at[year, 'SWP Withdrawal'] = withdrawal
    df.at[year, 'Custom Withdrawals'] = custom_withdrawal
    df.at[year, 'Adjusted End Balance'] = balance

    if year >= age_start:
        monthly_inv *= (1 + yearly_step_up / 100)

# Display Results
st.subheader('Investment Breakdown by Year')
st.dataframe(df.style.format(f"{currency_symbol}{{:,.0f}}"))

# Additional Insights
balance_age = st.sidebar.slider('Balance at Age', min_value=int(age_start), max_value=100, value=60, help='Age at which you want to see the adjusted balance.')
selected_balance = df.loc[balance_age, 'Adjusted End Balance']
st.metric(f"Balance at Age {balance_age} ({currency_symbol})", f"{currency_symbol}{selected_balance:,.0f}")
