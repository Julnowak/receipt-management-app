import decimal

from django.shortcuts import render,redirect,reverse
import pandas as pd
import datetime
from my_messages.models import Message
from categories.models import BaseCategories
from receipts.models import Receipt, Guarantee, Expense, User
from promotions_and_discounts.models import Shop
from groups.models import CommonGroups
import plotly.graph_objects as go
from django.contrib.auth.decorators import login_required


@login_required
def statistics(request):
    exps = Expense.objects.filter(owner=request.user)
    guarantees = Guarantee.objects.filter(owner=request.user)
    receipts = Receipt.objects.filter(owner=request.user)
    expenses = exps.filter(is_deleted=False).values_list("expense_name", "date_added", "amount","is_recurrent","number","time_stamp")
    recs = receipts.filter(is_deleted=False).values_list("receipt_name", "date_added", "amount")

    df_new = pd.DataFrame(list(expenses))
    df_new.columns = ["expense_name", "date_added", "amount","is_recurrent","number","time_stamp"]
    multiplier = 1

    # Ogólne
    year = []
    month = []
    day = []
    for i, row in df_new.iterrows():
        yk = str(row['date_added'])
        year += [int(yk[:4])]
        month += [int(yk[5:7])]
        day += [int(yk[8:10])]
        if row['is_recurrent']:

            newr = datetime.date(int(yk[:4]), int(yk[5:7]), int(yk[8:10]))
            if row['time_stamp'] == 'DNI':
                days_from = int((datetime.date.today() - newr).days)
                multiplier = days_from // int(row['number'])
            else:
                calc = 1
                years_from = int(datetime.date.today().year - newr.year)
                months_from = int(datetime.date.today().month - newr.month)
                if row['time_stamp'] == 'LAT':
                    calc = years_from//int(row['number'])
                elif row['time_stamp'] == 'MIESIĘCY':
                    calc = (years_from * 12 + months_from)//int(row['number'])

                if calc != 0:
                    multiplier = calc
            df_new.at[i, 'amount'] = decimal.Decimal(float(df_new.loc[i]['amount']) * multiplier)

    df_new['Year'] = year
    df_new['Month'] = month
    df_new['Day'] = day

    print(df_new)

    try:
        sum_exp = df_new['amount'].sum()
        sum_rec = pd.DataFrame(list(recs.values_list("amount"))).sum()[0]
        df_exp_rec = pd.DataFrame({'Rodzaj': ['Wydatki', 'Paragony'],
                                   'Suma': [sum_exp, sum_rec]})

        suma = sum_exp + sum_rec
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
            fig_pie_exp_rec.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0),height=500,
                                            legend=dict(orientation="h"), width=300)

            exp_rec_pie = fig_pie_exp_rec.to_html(full_html=False, include_plotlyjs=False)
    except:
        exp_rec_pie = "Nie dodano jeszcze żadnych wartości."


########################################################################

    df_rec = pd.DataFrame(list(recs))
    df_rec.columns = ["receipt_name", "date_added", "amount"]

    year_rec = []
    month_rec = []
    day_rec = []
    for i, row in df_rec.iterrows():
        yk = str(row['date_added'])
        year_rec += [int(yk[:4])]
        month_rec += [int(yk[5:7])]
        day_rec += [int(yk[8:10])]

    df_rec['Year'] = year_rec
    df_rec['Month'] = month_rec
    df_rec['Day'] = day_rec
    df_rec_by_year = df_rec[['Year', 'amount']].groupby('Year', as_index=False).sum()
    print(df_rec_by_year)
    try:
        if df_rec_by_year.empty:
            pie_years = "Brak danych z tego roku"
        else:
            fig_pie_years = go.Figure(go.Pie(
                name="",
                hole=0.5,
                values=df_rec_by_year['amount'],
                labels=df_rec_by_year['Year'],
                texttemplate="<br>%{value:.2f} zł <br> %{percent} </br>",
                textposition="inside",
            ))
            fig_pie_years.update_traces(marker=dict(colors=['#4f000b', '#720026', '#ce4257', '#ff7f51']))
            fig_pie_years.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0),height=500,
                                            legend=dict(orientation="h"), width=300)

            pie_years = fig_pie_years.to_html(full_html=False, include_plotlyjs=False)
    except:
        pie_years = "Nie dodano jeszcze żadnych wartości."

########################################################################

    df_rec_by_month = df_rec[['Month', 'amount']].groupby('Month', as_index=False).sum()
    print(df_rec_by_month)
    try:
        if df_rec_by_month.empty:
            pie_months = "Brak danych z tego roku"
        else:
            fig_pie_months = go.Figure(go.Pie(
                name="",
                hole=0.5,
                values=df_rec_by_month['amount'],
                labels=df_rec_by_month['Month'],
                texttemplate="<br>%{value:.2f} zł <br> %{percent} </br>",
                textposition="inside",
            ))
            fig_pie_months.update_traces(marker=dict(colors=['#4f000b', '#720026', '#ce4257', '#ff7f51']))
            fig_pie_months.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=500,
                                        legend=dict(orientation="h"), width=300)

            pie_months = fig_pie_months.to_html(full_html=False, include_plotlyjs=False)
    except:
        pie_months = "Nie dodano jeszcze żadnych wartości."

    ########################################################################


    context = {'guar_num': guarantees.count(),'guar_num_actual': guarantees.filter(is_deleted=False).count(), 'rec_num': receipts.filter().count(),
               'rec_num_actual': receipts.filter(is_deleted=False).count(),
               'exps_num': expenses.filter().count(),'exps_num_actual': expenses.filter(is_deleted=False).count(),
               "expen_num": expenses.count(),"exp_rec_pie":exp_rec_pie, 'user': request.user, 'suma': suma,
               'pie_years': pie_years, 'pie_months': pie_months}
    return render(request, "statistics_and_plots/statistics.html",context)


@login_required
def category_charts(request):
    exps = Expense.objects.filter(owner=request.user)
    expenses = exps.values_list("category", "amount")
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
        if df2.empty:
            pie_chart = "Brak danych"
        else:
            fig_pie = go.Figure(go.Pie(
                name="",
                hole=0.5,
                values=df2['amount'],
                labels=df2['category_name'],
                texttemplate="<br>%{value:.2f} zł <br> %{percent} </br>",
                textposition="inside",
            ))
            fig_pie.update_traces(marker=dict(colors=['#4f000b', '#720026', '#ce4257', '#ff7f51']))
            fig_pie.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=500, width=300,
                                          legend=dict(orientation="h"))

            pie_chart = fig_pie.to_html(full_html=False, include_plotlyjs=False)
    except:
        pie_chart = "Nie dodano jeszcze żadnych wartości."


    suma = df2['amount'].sum()

    context = {'user': request.user,"pie_chart": pie_chart, "suma": suma,}
    return render(request, "statistics_and_plots/category_charts.html", context)


@login_required
def groups_charts(request):
    groups = CommonGroups.objects.filter(members__username=request.user.username)
    receipts = Receipt.objects.filter(group__in=groups)
    expenses = Expense.objects.filter(group__in=groups)
    grps = groups.values_list('id','group_name', 'number_of_members')
    exps = expenses.filter(is_deleted=False).values_list("expense_name",'amount','group', "date_added","is_recurrent",
                                                                    "number", "time_stamp")
    recs = receipts.filter(is_deleted=False).values_list("receipt_name", "date_added", "amount",'group')

    df_new = pd.DataFrame(list(exps))

    df_new.columns = ["expense_name", 'amount', 'group', "date_added", "is_recurrent", "number", "time_stamp"]

    df_temp = pd.DataFrame(list(grps))
    df_temp.columns = ['group', 'group_name','number_of_members']
    df_new = pd.merge(df_new, df_temp, on=['group'])

    multiplier = 1

    # Ogólne
    year = []
    month = []
    day = []
    for i, row in df_new.iterrows():
        yk = str(row['date_added'])
        year += [int(yk[:4])]
        month += [int(yk[5:7])]
        day += [int(yk[8:10])]
        if row['is_recurrent']:

            newr = datetime.date(int(yk[:4]), int(yk[5:7]), int(yk[8:10]))
            if row['time_stamp'] == 'DNI':
                days_from = int((datetime.date.today() - newr).days)
                multiplier = days_from // int(row['number'])
            else:
                calc = 1
                years_from = int(datetime.date.today().year - newr.year)
                months_from = int(datetime.date.today().month - newr.month)
                if row['time_stamp'] == 'LAT':
                    calc = years_from // int(row['number'])
                elif row['time_stamp'] == 'MIESIĘCY':
                    calc = (years_from * 12 + months_from) // int(row['number'])

                if calc != 0:
                    multiplier = calc
            multiplier +=1
            df_new.at[i, 'amount'] = decimal.Decimal(float(df_new.loc[i]['amount']) * multiplier)

    df_new['Year'] = year
    df_new['Month'] = month
    df_new['Day'] = day

    df_recs = pd.DataFrame(list(recs))
    df_recs.columns = ["receipt_name", "date_added", "amount",'group']
    df_recs = pd.merge(df_recs, df_temp, on=['group'])
    df_new = pd.concat([df_recs, df_new], axis=0)

    for i, row in df_new.iterrows():
        df_new.at[i, 'amount'] = df_new['amount'][i]/df_new['number_of_members'][i]

    df_new = df_new[['group_name', 'amount']].groupby(['group_name'], as_index=False).sum()
    try:
        if df_new.empty:
            exp_rec_pie = "Brak danych z tego roku"
        else:
            fig_pie_exp_rec = go.Figure(go.Pie(
                name="",
                hole=0.5,
                values=df_new['amount'],
                labels=df_new['group_name'],
                texttemplate="<br>%{value:.2f} zł <br> %{percent} </br>",
                textposition="inside",
            ))
            fig_pie_exp_rec.update_traces(marker=dict(colors=['#4f000b', '#720026', '#ce4257', '#ff7f51']))
            fig_pie_exp_rec.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=500,
                                          legend=dict(orientation="h"), width=300)

            exp_rec_pie = fig_pie_exp_rec.to_html(full_html=False, include_plotlyjs=False)
    except:
        exp_rec_pie = "Nie dodano jeszcze żadnych wartości."

    suma = df_new['amount'].sum()
    ########################################################################

    context = {'rec_num': receipts.filter().count(),
               'rec_num_actual': receipts.filter(is_deleted=False).count(),
               'exps_num': expenses.filter().count(), 'exps_num_actual': expenses.filter(is_deleted=False).count(),
               "expen_num": expenses.count(), "exp_rec_pie": exp_rec_pie, 'user': request.user, 'suma': suma}
    return render(request, "statistics_and_plots/groups_charts.html", context)


@login_required
def shops_charts(request):
    shops = Shop.objects.all().values_list("id","shop_name")
    exps = Expense.objects.filter(owner=request.user)
    receipts = Receipt.objects.filter(owner=request.user)
    expenses = exps.filter(is_deleted=False).values_list("expense_name", "date_added", "amount", "is_recurrent",
                                                         "number", "time_stamp",'shop')
    recs = receipts.filter(is_deleted=False).values_list("receipt_name", "date_added", "amount",'shop')

    df_new = pd.DataFrame(list(expenses))
    df_new.columns = ["expense_name", "date_added", "amount", "is_recurrent", "number", "time_stamp", 'shop']
    multiplier = 1

    # Sklepy
    year = []
    month = []
    day = []
    for i, row in df_new.iterrows():
        yk = str(row['date_added'])
        year += [int(yk[:4])]
        month += [int(yk[5:7])]
        day += [int(yk[8:10])]
        if row['is_recurrent']:

            newr = datetime.date(int(yk[:4]), int(yk[5:7]), int(yk[8:10]))
            if row['time_stamp'] == 'DNI':
                days_from = int((datetime.date.today() - newr).days)
                multiplier = days_from // int(row['number'])
            else:
                calc = 1
                years_from = int(datetime.date.today().year - newr.year)
                months_from = int(datetime.date.today().month - newr.month)
                if row['time_stamp'] == 'LAT':
                    calc = years_from // int(row['number'])
                elif row['time_stamp'] == 'MIESIĘCY':
                    calc = (years_from * 12 + months_from) // int(row['number'])

                if calc != 0:
                    multiplier = calc
            df_new.at[i, 'amount'] = decimal.Decimal(float(df_new.loc[i]['amount']) * multiplier)

    df_new['Year'] = year
    df_new['Month'] = month
    df_new['Day'] = day

    df_rec = pd.DataFrame(list(recs))
    df_rec.columns = ["receipt_name", "date_added", "amount",'shop']
    df_shops = pd.DataFrame(list(shops))
    df_shops.columns = ["shop", 'shop_name']
    df_rec = pd.merge(df_rec, df_shops, on=['shop'])

    df_new['shop'].fillna(Shop.objects.get(shop_name="Inne").id, inplace=True)
    df_new = pd.merge(df_new, df_shops, on=['shop'])
    df_rec = pd.concat([df_new, df_rec], axis=0)
    df_rec = df_rec[['shop_name', 'amount']].groupby('shop_name', as_index=False).sum()
    try:

        if df_rec.empty:
            exp_rec_pie = "Brak danych z tego roku"
        else:
            fig_pie_exp_rec = go.Figure(go.Pie(
                name="",
                hole=0.5,
                values=df_rec['amount'],
                labels=df_rec['shop_name'],
                texttemplate="<br>%{value:.2f} zł <br> %{percent} </br>",
                textposition="inside",
            ))
            fig_pie_exp_rec.update_traces(marker=dict(colors=['#4f000b', '#720026', '#ce4257', '#ff7f51']))
            fig_pie_exp_rec.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=500,
                                          legend=dict(orientation="h"), width=300)

            exp_rec_pie = fig_pie_exp_rec.to_html(full_html=False, include_plotlyjs=False)
    except:
        exp_rec_pie = "Nie dodano jeszcze żadnych wartości."

    suma = df_rec['amount'].sum()


    ########################################################################

    context = {'rec_num': receipts.filter().count(),
               'rec_num_actual': receipts.filter(is_deleted=False).count(),
               'exps_num': expenses.filter().count(), 'exps_num_actual': expenses.filter(is_deleted=False).count(),
               "expen_num": expenses.count(), "exp_rec_pie": exp_rec_pie, 'user': request.user, 'suma': suma
               }
    return render(request, "statistics_and_plots/shops_charts.html", context)