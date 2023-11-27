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
    exps = Expense.objects.filter(owner=request.user)
    guarantees = Guarantee.objects.filter(owner=request.user)
    receipts = Receipt.objects.filter(owner=request.user)
    expenses = exps.values_list("category", "amount")
    expenses_2 = exps.values_list("date_added", "amount","is_recurrent","time_stamp")

    e = pd.DataFrame(list(expenses.values_list("amount"))).sum()[0]
    g = 0
    r = 0

    suma = e+g+r
    dropdown_buttons = []

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

        for i in df2['category_name']:
            dropdown_buttons.append({'label': i,
                                     'method': 'update',
                                     'args': [{'showlegend': True}]
                                     })

        fig_pie.update_layout({
                           'updatemenus': [{'type': 'dropdown', 'buttons': dropdown_buttons}],
                           })

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
        fig_pie_exp_rec = px.pie(df_exp_rec, values='Suma', names='Rodzaj', height=300, title="Rozkład wydatków")

        exp_rec_pie = fig_pie_exp_rec.to_html(full_html=False, include_plotlyjs=False)

        labels_exp_rec = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]

    except:
        exp_rec_pie = "Nie dodano jeszcze żadnych wartości."
        labels_exp_rec = "Brak"


    context = {"pie_chart": pie_chart, 'labels': labels,'guar_num': guarantees.count(), 'rec_num': receipts.count(),
               "expen_num": expenses.count(), "suma": suma,"exp_rec_pie":exp_rec_pie, "labels_exp_rec": labels_exp_rec}
    return render(request, "statistics_and_plots/statistics.html",context)