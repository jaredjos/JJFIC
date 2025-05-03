import streamlit as st
import pandas as pd
import numpy as np

st.title("Jared's Financial Independence Calculator 📈")

# User Inputs
st.sidebar.header('Investment Parameters')

# Currency Selector
currency_symbol = st.sidebar.selectbox('Select Currency', ['₹', '$', '€', '£', '¥'])

age_start = st.sidebar.number_input('Starting Age', min_value=18, max_value=100, value=30)
age_end = st.sidebar.number_input('Ending Age (Investment Stop)', min_value=age_start, max_value=100, value=45)
age_retire = st.sidebar.number_input('Retirement Age (SWP Start)', min_value=age_end, max_value=100, value=60)

initial_lump_sum = st.sidebar.number_input(f'Initial Lump Sum ({currency_symbol})', min_value=0, value=500000)
monthly_investment = st.sidebar.number_input(f'Initial Monthly Investment ({currency_symbol})', min_value=0, value=50000)
yearly_step_up = st.sidebar.slider('Annual Step-Up (%)', min_value=0.0, max_value=20.0, value=5.0, step=0.5)

annual_return = st.sidebar.slider('Annual Return (%)', min_value=1.0, max_value=50.0, value=12.0, step=0.5)
annual_inflation = st.sidebar.slider('Annual Inflation (%)', min_value=0.0, max_value=15.0, value=6.0, step=0.5)
swp_inflation = st.sidebar.slider('SWP Annual Inflation (%)', min_value=0.0, max_value=15.0, value=6.0, step=0.5)

swp_monthly_withdrawal = st.sidebar.number_input(f'Monthly SWP Amount ({currency_symbol})', min_value=0, value=100000)

# Custom Investments
st.sidebar.subheader('Custom Lump Sum Investments')
custom_investments = []
num_custom_investments = st.sidebar.number_input('Number of Custom Investments', min_value=0, max_value=10, value=0)

for i in range(int(num_custom_investments)):
    st.sidebar.write(f'Custom Investment {i+1}')
    year = st.sidebar.number_input(f'Year of Investment {i+1}', min_value=age_start, max_value=100, value=age_start)
    amount = st.sidebar.number_input(f'Amount {i+1} ({currency_symbol})', min_value=0, value=100000)
    growth = st.sidebar.slider(f'Growth Rate {i+1} (%)', min_value=1.0, max_value=50.0, value=12.0, step=0.5)
    custom_investments.append((year, amount, growth))

# Calculation logic
years = np.arange(age_start, 101)
df = pd.DataFrame(index=years, columns=['Age', 'Year Start Balance', 'Annual Investment', 'Custom Investments', 'Year End Balance', 'SWP Withdrawal', 'Adjusted End Balance'])
df['Age'] = years

balance = initial_lump_sum
monthly_inv = monthly_investment
current_swp = swp_monthly_withdrawal
custom_balance = {year: 0 for year in years}

for custom_year, amount, growth in custom_investments:
    custom_balance[custom_year] += amount

for year in years:
    annual_investment = monthly_inv * 12 if age_start <= year < age_end else 0
    custom_investment = custom_balance[year]

    balance = balance * (1 + annual_return / 100) + annual_investment
    balance += custom_investment

    df.at[year, 'Year Start Balance'] = balance - annual_investment - custom_investment
    df.at[year, 'Annual Investment'] = annual_investment
    df.at[year, 'Custom Investments'] = custom_investment
    df.at[year, 'Year End Balance'] = balance

    if year >= age_retire:
        withdrawal = current_swp * 12
        balance -= withdrawal
        df.at[year, 'SWP Withdrawal'] = withdrawal
        current_swp *= (1 + swp_inflation / 100)
    else:
        df.at[year, 'SWP Withdrawal'] = 0

    df.at[year, 'Adjusted End Balance'] = balance

    if year >= age_start:
        monthly_inv *= (1 + yearly_step_up / 100)

# Display Results
st.subheader('Investment Breakdown by Year')
st.dataframe(df.style.format(f"{currency_symbol}{{:,.0f}}"))

# Plotting
st.subheader('Investment Growth Over Time')
st.line_chart(df[['Year End Balance', 'Adjusted End Balance']])

st.subheader('Adjusted Growth Over Time (Post SWP)')
st.line_chart(df['Adjusted End Balance'])

st.subheader('SWP Withdrawals Over Time')
st.bar_chart(df['SWP Withdrawal'])

# Additional Insights
final_balance = df.loc[100, 'Adjusted End Balance']
st.metric(f"Final Balance at Age 100 ({currency_symbol})", f"{currency_symbol}{final_balance:,.0f}")
