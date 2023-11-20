from django.shortcuts import render,redirect,reverse
import pandas as pd
from datetime import datetime
from my_messages.models import Message
from categories.models import BaseCategories
from receipts.models import Receipt, Guarantee, Expense
import plotly.express as px
import plotly.graph_objects as go
from sklearn.datasets import load_iris


def statistics(request):
    data = load_iris(as_frame=True)
    df = data['data']
    df['target'] = data['target']
    target_map = {0: 'setosa', 1: 'versicolor', 2: 'virginica'}
    df['target_name'] = df['target'].apply(lambda x: target_map[x])
    df.head()
    names = list(df['target_name'].unique())
    fig = go.Figure()
    dropdown_buttons = []
    x_col = 'sepal length (cm)'
    y_col = 'petal length (cm)'
    min_x, max_x = df[x_col].min(), df[x_col].max()
    min_y, max_y = df[y_col].min(), df[y_col].max()

    for i, nm in enumerate(names):
        tmp_df = df[df['target_name'] == nm]
        fig.add_trace(go.Scatter(x=tmp_df['sepal length (cm)'],
                                 y=tmp_df['petal length (cm)'],
                                 mode='markers',
                                 name=nm))
        visibility = ['legendonly'] * len(names)
        visibility[i] = True
        dropdown_buttons.append({'label': nm,
                                 'method': 'update',
                                 'args': [{'visible': visibility, 'title': nm, 'showlegend': True}]
                                 })

    dropdown_buttons.insert(0, {'label': 'All',
                                'method': 'update',
                                'args': [{'visible': [True] * len(names), 'title': 'All', 'showlegend': True}]
                                })
    fig.update_layout({'width': 800,
                       'height': 400,
                       'yaxis_range': [min_y - 0.5, max_y + 0.5],
                       'xaxis_range': [min_x - 0.5, max_x + 0.5],
                       'updatemenus': [{'type': 'dropdown', 'buttons': dropdown_buttons}],
                       })

    fig = fig.to_html(full_html=False, include_plotlyjs=False)

    exps = Expense.objects.filter(owner=request.user)
    guarantees = Guarantee.objects.filter(owner=request.user)
    receipts = Receipt.objects.filter(owner=request.user)
    expenses = exps.values_list("category", "amount")
    expenses_2 = exps.values_list("date_added", "amount","is_recurrent","time_stamp")

    e = pd.DataFrame(list(expenses.values_list("amount"))).sum()[0]
    g = 0
    r = 0

    suma = e+g+r

    dates_added = Expense.objects.filter(owner=request.user).values_list("date_added")
    categories = BaseCategories.objects.values_list("id", "category_name")

    # Pie Chart
    try:
        df = pd.DataFrame(list(expenses))
        df.columns = ['category', 'amount']
        df_temp = pd.DataFrame(list(categories))
        df_temp.columns = ['category', 'category_name']
        df2 = pd.merge(df, df_temp, on=['category'])
        fig_pie = px.pie(df2, values='amount', names='category_name', height=300, title="Wydatki stałe")

        pie_chart = fig_pie.to_html(full_html=False, include_plotlyjs=False)

        labels = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]

    except:
        pie_chart = "Nie dodano jeszcze żadnych wartości."
        labels = "Brak"

    # Pie Chart for amounts
    try:
        sum_exp = 0
        for exp in expenses_2:
            multiplier = 1

            # Jeśli wydatek powtarzalny
            if exp[2]:
                u = datetime.today().date() - exp[0].date()
                if exp[3] == 'TYGODNI':
                    multiplier = u.days//7
                elif exp[3] == 'MIESIĘCY':
                    #################################### UWAGA
                    multiplier = u.days // 30
                elif exp[3] == 'LAT':
                    multiplier = u.days // 365
                multiplier += 1
            sum_exp += exp[1] * multiplier

        sum_rec = pd.DataFrame(list(receipts.values_list("amount"))).sum()[0]

        df_exp_rec = pd.DataFrame({'Rodzaj': ['Wydatki', 'Paragony'],
                                   'Suma': [sum_exp, sum_rec]})
        print(df_exp_rec)
        fig_pie_exp_rec = px.pie(df_exp_rec, values='Suma', names='Rodzaj', height=300, title="Rozkład wydatków")

        exp_rec_pie = fig_pie_exp_rec.to_html(full_html=False, include_plotlyjs=False)

        labels_exp_rec = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]

    except:
        exp_rec_pie = "Nie dodano jeszcze żadnych wartości."
        labels_exp_rec = "Brak"


    context = {"pie_chart": pie_chart, 'labels': labels,'guar_num': guarantees.count(), 'rec_num': receipts.count(),
               "expen_num": expenses.count(), "suma": suma,"exp_rec_pie":exp_rec_pie, "labels_exp_rec": labels_exp_rec,
               'fig':fig}
    return render(request, "statistics_and_plots/statistics.html",context)