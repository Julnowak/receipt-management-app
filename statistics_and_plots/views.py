from django.shortcuts import render,redirect,reverse
import pandas as pd
from datetime import datetime
from my_messages.models import Message
from categories.models import BaseCategories
from receipts.models import Receipt, Guarantee, Expense
from promotions_and_discounts.models import Shop
import plotly.express as px
import plotly.graph_objects as go


from django.contrib.auth.decorators import login_required
@login_required
def statistics(request):
    exps = Expense.objects.filter(owner=request.user)
    guarantees = Guarantee.objects.filter(owner=request.user)
    shops = Shop.objects.all()
    receipts = Receipt.objects.filter(owner=request.user)
    expenses = exps.values_list("category", "amount")
    expenses_2 = exps.values_list("date_added", "amount","is_recurrent","time_stamp")


    e = pd.DataFrame(list(expenses.values_list("amount"))).sum()[0]
    g = 0
    r = 0

    suma = e+g+r
    categories = BaseCategories.objects.values_list("id", "category_name")

    # Pie Chart
    try:
        df = pd.DataFrame(list(expenses))
        df.columns = ['category', 'amount']
        df_temp = pd.DataFrame(list(categories))
        df_temp.columns = ['category', 'category_name']
        df2 = pd.merge(df, df_temp, on=['category'])

        fig_pie = px.pie(df2, values='amount', names='category_name', height=300, title="Wydatki stałe")

        dropdown_options = []
        for i in df2['category_name'].drop_duplicates():
            print(i)
            dropdown_options.append({'label': i,
                                     "method": "update",
                                     "args": [{"visible": i}],
                                     })


        # Add dropdown to the layout
        fig_pie.update_layout(
            updatemenus=[
                {
                    'buttons': dropdown_options,
                    'direction': 'down',
                    'pad': {'r': 10, 't': 10},
                    'showactive': True,
                    'x': 0.1,
                    'xanchor': 'left',
                    'y': 1.1,
                    'yanchor': 'top'
                },
            ],
        )

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

        if df_exp_rec.empty:
            exp_rec_pie = "Brak danych z tego roku"
        else:
            fig_pie_exp_rec = go.Figure(go.Pie(
                name="",
                hole=0.5,
                values=df_exp_rec['Suma'],
                labels=df_exp_rec['Rodzaj'],
                texttemplate="<br>%{value:.2f} zł <br> %{percent} </br>",
                textposition="inside",
            ))
            fig_pie_exp_rec.update_traces(marker=dict(colors=['#4f000b', '#720026', '#ce4257', '#ff7f51']))
            fig_pie_exp_rec.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0),
                                       legend=dict(orientation="h"))

            exp_rec_pie = fig_pie_exp_rec.to_html(full_html=False, include_plotlyjs=False)
    except:
        exp_rec_pie = "Nie dodano jeszcze żadnych wartości."

    context = {"pie_chart": pie_chart, 'labels': labels,'guar_num': guarantees.count(), 'rec_num': receipts.count(),
               "expen_num": expenses.count(), "suma": suma,"exp_rec_pie":exp_rec_pie, }
    return render(request, "statistics_and_plots/statistics.html",context)


def category_charts(request):
    context = {}
    return render(request, "statistics_and_plots/category_charts.html", context)