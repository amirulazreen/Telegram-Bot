import matplotlib.pyplot as plt
import pandas as pd
import io
from io import BytesIO
from telegram import Update
from telegram.ext import Application, Updater, CommandHandler, MessageHandler, CallbackContext, filters, ContextTypes
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta, time
import numpy as np
import source

"""
    graph1 - Blood Donations Trend - Malaysia
    graph2 - Blood Donors Retention - Malaysia
    graph3 - Blood Donations Trend - States
    graph4 - Number Of Blood Donations per Hospital
    graph5 - Correlation Between Accessibility And Number of Blood Donation
    graph6 - Number of Blood Donations Based On Social Group
    graph7 - Number of Blood Donations Based On Blood Type
    graph8 - Number Of New Blood Donors Based On Age Groups
    graph9 - Blood Donors Scatterplot
"""

async def graph1(bot=None, update=None, context=None):
    source.c["date"] = pd.to_datetime(source.c['date'])
    source.c['year'] = source.c['date'].dt.year
    year = source.c.groupby(["year", "state"]).agg({'daily': 'sum'}).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    state_data = year[year['state'] == "Malaysia"]
    ax.plot(state_data['year'], state_data['daily'])
    ax.set_xticks(state_data['year'][::3])
    ax.set_title('Blood Donations Trend - Malaysia')
    ax.set_xlabel('Year')
    ax.set_ylabel('Total Donations Per Year')
    ax.legend()
    ax.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

async def graph2(bot=None, update=None, context=None):
    source.c["date"] = pd.to_datetime(source.c['date'])
    source.c['year'] = source.c['date'].dt.year
    grouped_df = source.c.groupby('year').agg({'donations_new': 'sum', 'donations_regular': 'sum', 'donations_irregular': 'sum'}).reset_index()

    plt.figure(figsize=(10, 6))

    plt.plot(grouped_df['year'], grouped_df['donations_new'], label='New Donor', color='blue', alpha=0.7)
    plt.plot(grouped_df['year'], grouped_df['donations_regular'], label='Regular Donor', color='green', alpha=0.7)
    plt.plot(grouped_df['year'], grouped_df['donations_irregular'], label='Irregular Donor', color='orange', alpha=0.7)

    plt.title('Blood Donor Retentions Trends')
    plt.xlabel('Year')
    plt.ylabel('Total Number of Donors')
    plt.legend()
    plt.grid(True)
    plt.xticks(grouped_df['year'][::3])

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

async def graph3(bot=None, update=None, context=None):
    source.c["date"] = pd.to_datetime(source.c['date'])
    source.c['year'] = source.c['date'].dt.year
    year = source.c.groupby(["year", "state"]).agg({'daily': 'sum'}).reset_index()
    states_to_plot = year[year['state'] != "Malaysia"]['state'].unique()

    fig, ax = plt.subplots(figsize=(14, 8))
    palette = sns.color_palette('rainbow', n_colors=len(states_to_plot))

    for i, state in enumerate(states_to_plot):
        state_data = year[year['state'] == state]
        ax.plot(state_data['year'], state_data['daily'], label=state, marker='o', linestyle='-', color=palette[i])

    ax.set_title('Blood Donations Trend - States', fontsize=16)
    ax.set_xlabel('Year', fontsize=14)
    ax.set_ylabel('Total Donations Per Year', fontsize=14)
    legend = ax.legend(loc='upper left', bbox_to_anchor=(0.98, 1), title='State', fontsize='x-small')
    ax.set_xticks(state_data['year'][::3])
    ax.grid(True)
    ax.tick_params(axis='both', which='major', labelsize=12)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

async def graph4(bot=None, update=None, context=None):
    grouped_df = source.b.groupby('hospital').agg({'daily': 'sum'}).reset_index()

    def format_ticks(x, _):
        if x == 0:
            return 0
        elif x < 1e3:
            return f'{int(x)}'
        elif x < 1e6:
            return f'{int(x/1e3)}k'
        else:
            return f'{round(x/1e6, 1)}k'

    plt.figure(figsize=(23, 10))
    plt.barh(grouped_df['hospital'], grouped_df['daily'],color='deepskyblue')
    plt.title('Number of blood donations per hospital')
    plt.xlabel('Number of blood donations')
    plt.gca().xaxis.set_major_formatter(FuncFormatter(format_ticks))
    tick_spacing = 200000
    plt.xticks(range(0, int(max(grouped_df['daily'])) + tick_spacing, tick_spacing))
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

async def graph5(bot=None, update=None, context=None):
    grouped_df = source.b.groupby('hospital').agg({'daily': 'sum'}).reset_index()

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=source.b['location_mobile'], y=source.b['daily'], hue=source.b['hospital'], palette='viridis', legend='full')
    plt.xlabel('Number of blood donations via mobile')
    plt.ylabel('Number of blood donations')
    plt.title('Correlation between accessibility and number of blood donations')
    plt.legend(title='Hospital', bbox_to_anchor=(1.05, 1), loc='upper left')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    return buffer

async def graph6(bot=None, update=None, context=None):
    x = source.c.rename(columns={
        'social_civilian': 'Civilian',
        'social_student': 'Student',
        'social_policearmy': 'Uniformed Bodies'
    })

    column_sums = x[['Civilian', 'Student', 'Uniformed Bodies']].sum()

    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.barplot(x=column_sums.values, y=column_sums.index, color='deepskyblue')
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:,.0f}'.format(x)))
    plt.title('Number of blood donations based on social group')
    plt.xlabel('Number of blood donations')
    plt.ylabel('')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

async def graph7(bot=None, update=None, context=None):
    column_sums = source.c[['blood_a', 'blood_b', 'blood_o', 'blood_ab']].sum()

    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.barplot(x=column_sums.values, y=column_sums.index, color='deepskyblue')
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:,.0f}'.format(x)))
    plt.title('Number of blood donations based on blood types')
    plt.xlabel('Number of blood donations')
    plt.ylabel('Blood type')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

async def graph8(bot=None, update=None, context=None):
    column_sums = source.e[['17-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', 'other']].sum()

    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.barplot(x=column_sums.values, y=column_sums.index, color='deepskyblue')
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:,.0f}'.format(x)))
    plt.title('Number of new blood donors based on age groups')
    plt.xlabel('Number of blood donations')
    plt.ylabel('Age group')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

async def graph9(bot=None, update=None, context=None):
    two_years_ago = pd.Timestamp.now() - pd.Timedelta(days=365 * 2)
    three_months_ago = pd.Timestamp.now() - pd.Timedelta(days=30 * 3)

    conditions = [
        (source.visit_counts['min'] >= three_months_ago) & (source.visit_counts['max'] >= three_months_ago) & (source.visit_counts['count'] == 1),
        (source.visit_counts['min'] <= two_years_ago) & (source.visit_counts['max'] >= two_years_ago),
        (source.visit_counts['min'] <= three_months_ago) & (source.visit_counts['max'] >= two_years_ago) & (source.visit_counts['count'] == 1),
        (source.visit_counts['min'] <= two_years_ago) & (source.visit_counts['max'] <= two_years_ago)
    ]

    categories = ['new donor', 'old active donor', 'irregular donor', 'lapsed donor']

    source.visit_counts['category'] = np.select(conditions, categories, default='regular donor')

    category_colors = {
        'new donor': '#00ff00',
        'old active donor': '#89cff0',
        'irregular donor': '#ff0000',
        'lapsed donor': '#2e8b57',
        'regular donor': '#0054a6'
    }

    plt.figure(figsize=(10, 6))
    for category, color in category_colors.items():
        category_data = source.visit_counts[source.visit_counts['category'] == category]
        plt.scatter(category_data['min'], category_data['max'], c=color, label=category, s=50, alpha=0.5)

    plt.xlabel('1st Blood Donation')
    plt.ylabel('Last Blood Donation')
    plt.title('Blood Donors Retention Scatterplot')
    plt.legend()
    plt.grid(True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

