import decimal

from django.shortcuts import render,redirect,reverse
import pandas as pd
import datetime
from categories.models import BaseCategories
from receipts.models import Receipt, Guarantee, Expense, User
from promotions_and_discounts.models import Shop
from groups.models import CommonGroups
import plotly.graph_objects as go
from django.contrib.auth.decorators import login_required
import math
import plotly.express as px

def month_map(num):
    months = {
        1: 'Styczeń',
        2: 'Luty',
        3: 'Marzec',
        4: 'Kwiecień',
        5: 'Maj',
        6: 'Czerwiec',
        7: 'Lipiec',
        8: 'Sierpień',
        9: 'Wrzesień',
        10: 'Październik',
        11: 'Listopad',
        12: 'Grudzień'
    }
    return months[num]


def calculate_recurrent_expense(df):
    multiplier = 1

    # Ogólne
    year = []
    month = []
    day = []
    for i, row in df.iterrows():
        yk = str(row['date_added'])
        year += [int(yk[:4])]
        month += [int(yk[5:7])]
        day += [int(yk[8:10])]
        if row['is_recurrent']:
            end = datetime.date.today()
            newr = datetime.date(int(yk[:4]), int(yk[5:7]), int(yk[8:10]))
            if row['time_stamp'] == 'DNI':
                days_from = int((end - newr).days)
                multiplier = days_from // int(row['number'])
            else:
                calc = 1
                years_from = int(end.year - newr.year)
                months_from = int(end.month - newr.month)
                if row['time_stamp'] == 'LAT':
                    calc = years_from // int(row['number'])
                elif row['time_stamp'] == 'MIESIĘCY':
                    calc = (years_from * 12 + months_from) // int(row['number'])

                if calc != 0:
                    multiplier = calc
            multiplier += 1
            df.at[i, 'amount'] = decimal.Decimal(float(df.loc[i]['amount']) * multiplier)

    df['Year'] = year
    df['Month'] = month
    df['Day'] = day
    return df


def calculate_date(df):
    # Ogólne
    year = []
    month = []
    day = []
    for i, row in df.iterrows():
        yk = str(row['date_added'])
        year += [int(yk[:4])]
        month += [int(yk[5:7])]
        day += [int(yk[8:10])]

    df['Year'] = year
    df['Month'] = month
    df['Day'] = day
    return df


@login_required
def statistics(request):
    suma = 0
    expenses = Expense.objects.filter(owner=request.user)
    guarantees = Guarantee.objects.filter(owner=request.user)
    receipts = Receipt.objects.filter(owner=request.user)
    exps = expenses.filter(is_deleted=False).values_list("expense_name", "date_added", "amount","is_recurrent","number","time_stamp")
    recs = receipts.filter(is_deleted=False).values_list("receipt_name", "date_added", "amount")
    sum_exp_norec = 0
    sum_exp_rec = 0
    sum_rec = 0
    if exps:
        df_new = pd.DataFrame(list(exps))
        df_new.columns = ["expense_name", "date_added", "amount", "is_recurrent", "number", "time_stamp"]
        df_new = calculate_recurrent_expense(df_new)
        sum_exp_norec = df_new['amount'][df_new['is_recurrent'] == False].sum()
        sum_exp_rec = df_new['amount'][df_new['is_recurrent'] == True].sum()
    if recs:
        sum_rec = pd.DataFrame(list(recs.values_list("amount"))).sum()[0]

    df_exp_rec = pd.DataFrame({'Rodzaj': ['Opłaty jednorazowe', 'Opłaty powtarzalne', 'Paragony'],
                                'Suma': [sum_exp_norec, sum_exp_rec, sum_rec]})


    try:
        suma = sum_rec + sum_exp_norec + sum_exp_rec
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

    if exps:
        df_exp = pd.DataFrame(list(exps))
        df_exp.columns = ["expense_name", "date_added", "amount", "is_recurrent", "number", "time_stamp"]
        df_exp = calculate_recurrent_expense(df_exp)
        year_rec = []
        month_rec = []
        day_rec = []
        for i, row in df_exp.iterrows():
            yk = str(row['date_added'])
            year_rec += [int(yk[:4])]
            month_rec += [int(yk[5:7])]
            day_rec += [int(yk[8:10])]

        df_exp['Year'] = year_rec
        df_exp['Month'] = month_rec
        df_exp['Day'] = day_rec

    if recs:
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

    if exps and recs:
        new_df = pd.concat([df_exp, df_rec])
    elif exps:
        new_df = df_exp.copy()
    elif recs:
        new_df = df_rec.copy()

    try:
        df_rec_by_year = new_df[['Year', 'amount']].groupby('Year', as_index=False).sum()
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

    try:
        df_rec_by_month = new_df[['Month', 'amount']].groupby('Month', as_index=False).sum()
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
            month_list = []
            for m in df_rec_by_month['Month']:
                month_list.append(month_map(m))

            df_rec_by_month['month_name'] = month_list

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
    exps = Expense.objects.filter(owner=request.user, is_deleted=False)
    receipts = Receipt.objects.filter(owner=request.user, is_deleted=False)
    if exps:
        df = pd.DataFrame(list(exps.values_list("category", "amount", "date_added", "is_recurrent","number", "time_stamp",)))
        df.columns = ["category", "amount", "date_added", "is_recurrent","number", "time_stamp",]
        df = calculate_recurrent_expense(df)
        year_rec = []
        month_rec = []
        day_rec = []
        for i, row in df.iterrows():
            yk = str(row['date_added'])
            year_rec += [int(yk[:4])]
            month_rec += [int(yk[5:7])]
            day_rec += [int(yk[8:10])]
        df['Year'] = year_rec
        df['Month'] = month_rec
        df['Day'] = day_rec


    if receipts:
        r = pd.DataFrame(list(receipts.values_list("receipt_categories", "amount", "date_added")))
        r.columns = ['category', 'amount', "date_added"]
        year_rec = []
        month_rec = []
        day_rec = []
        for i, row in r.iterrows():
            yk = str(row['date_added'])
            year_rec += [int(yk[:4])]
            month_rec += [int(yk[5:7])]
            day_rec += [int(yk[8:10])]

        r['Year'] = year_rec
        r['Month'] = month_rec
        r['Day'] = day_rec


    suma = 0
    categories = BaseCategories.objects.values_list("id", "category_name")
    df_temp = pd.DataFrame(list(categories))
    df_temp.columns = ['category', 'category_name']
    if not df.empty and not r.empty:
        df2 = pd.concat([df, r])
    elif r:
        df2 = r
    elif df:
        df2 = df

    new = df2.copy()

    # Pie Chart
    try:

        df2 = pd.merge(df2, df_temp, on=['category'])
        df2 = df2[['category_name', 'amount']].groupby("category_name", as_index=False).sum()

        suma = df2['amount'].sum()
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

    #########################################################

    df2 = pd.merge(new, df_temp, on=['category'])
    df2 = df2[['category_name', 'amount', 'Year']].groupby(["category_name","Year"], as_index=False).sum()

    df2['Year'] = df2['Year'].astype(str)
    df2_prev = df2.copy()
    if len(df2_prev) >= 3:
        for i in df2['Year'].unique():
            a = pd.DataFrame({"category_name" :["Pozostałe"], 'amount':[df2_prev[df2['Year'] == i]['amount'][3:].sum()], 'Year': i})
            df2 = pd.concat([df2[df2['Year'] == i][:3], a])

    sumaR = df2['amount'].sum()
    if df2.empty:
        pie_chart_year = "Brak danych"
    else:
        fig_pie_year = px.bar(df2, y='amount', x='Year', color='category_name', text='amount',
                              labels={
                                  "amount": "Kwota [zł]",
                                  "Year": "Rok",
                                  "category_name": "Kategoria"
                              },
                              )

        fig_pie_year.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=500, width=300,
                              legend=dict(orientation="h"))

        fig_pie_year.update_traces(texttemplate='%{text:.2f} zł', textposition='outside')

        pie_chart_year = fig_pie_year.to_html(full_html=False, include_plotlyjs=False)

        #########################################################
        # Pie Chart
        df2 = pd.merge(new, df_temp, on=['category'])
        df2 = df2[['category_name', 'amount', 'Month']].groupby(["category_name", "Month"], as_index=False).sum()

        df2['Month'] = df2['Month'].astype(str)

        lista = []
        df2_prev = df2.copy()
        if len(df2_prev) >= 3:
            for i in df2['Month'].unique():
                a = pd.DataFrame(
                    {"category_name": ["Pozostałe"], 'amount': [df2_prev[df2['Month'] == i]['amount'][3:].sum()],
                     'Month': i})
                df_new = pd.concat([df2[df2['Month'] == i][:3], a])
                lista += [df_new]

            df2 = pd.concat(lista)

        sumaM = df2['amount'].sum()
        if df2.empty:
            pie_chart_month = "Brak danych"
        else:
            fig_pie_month = px.bar(df2, y='amount', x='Month', color='category_name', text='amount',
                                   labels={
                                       "amount": "Kwota [zł]",
                                       "Month": "Miesiąc",
                                       "category_name": "Kategoria"
                                   },
                                   )

            fig_pie_month.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=500, width=300,
                                       legend=dict(orientation="h"))

            fig_pie_month.update_traces(texttemplate='%{text:.2f} zł', textposition='outside')

            pie_chart_month = fig_pie_month.to_html(full_html=False, include_plotlyjs=False)

    context = {'user': request.user,"pie_chart": pie_chart, "suma": suma, "sumaR": sumaR, "sumaM": sumaM,
               "pie_chart_year": pie_chart_year,"pie_chart_month": pie_chart_month,}
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
    if grps:
        df_temp = pd.DataFrame(list(grps))
        df_temp.columns = ['group', 'group_name','number_of_members']

    if exps:
        df_exp = pd.DataFrame(list(exps))
        df_exp.columns = ["expense_name", 'amount', 'group', "date_added", "is_recurrent", "number", "time_stamp"]
        df_exp = calculate_recurrent_expense(df_exp)
        df_exp = pd.merge(df_exp, df_temp, on=['group'])

    if recs:
        df_recs = pd.DataFrame(list(recs))
        df_recs.columns = ["receipt_name", "date_added", "amount",'group']
        df_recs = pd.merge(df_recs, df_temp, on=['group'])

    if recs and exps:
        df_new = pd.concat([df_recs, df_exp], axis=0)
    elif recs:
        df_new = df_recs
    elif exps:
        df_new = df_exp

    df_prev = df_new.copy()
    df_new = df_new[['amount','group_name','number_of_members']].groupby(['group_name', 'number_of_members'], as_index=False).sum()
    try:
        for i, row in df_new.iterrows():
            df_new.at[i, 'amount'] = math.ceil(df_new['amount'][i] / df_new['number_of_members'][i] * 100) / 100

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
    print(df_prev)
    for i,row in df_prev.iterrows():
        if not row['Year'] and not row['Month'] and not row['Day']:
            dat = str(row['date_added'])
            print(dat)

    df_new = df_new[['amount','group_name','number_of_members']].groupby(['group_name', 'number_of_members'], as_index=False).sum()

    try:
        for i, row in df_new.iterrows():
            df_new.at[i, 'amount'] = math.ceil(df_new['amount'][i] / df_new['number_of_members'][i] * 100) / 100

        if df_new.empty:
            pie_chart_year = "Brak danych z tego roku"
        else:
            fig_pie_chart_year = go.Figure(go.Pie(
                name="",
                hole=0.5,
                values=df_new['amount'],
                labels=df_new['group_name'],
                texttemplate="<br>%{value:.2f} zł <br> %{percent} </br>",
                textposition="inside",
            ))
            fig_pie_chart_year.update_traces(marker=dict(colors=['#4f000b', '#720026', '#ce4257', '#ff7f51']))
            fig_pie_chart_year.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0), height=500,
                                          legend=dict(orientation="h"), width=300)

            pie_chart_year = fig_pie_chart_year.to_html(full_html=False, include_plotlyjs=False)
    except:
        pie_chart_year = "Nie dodano jeszcze żadnych wartości."

    sumaR = df_new['amount'].sum()
    ########################################################################

    context = {'rec_num': receipts.filter().count(),
               'rec_num_actual': receipts.filter(is_deleted=False).count(),
               'exps_num': expenses.filter().count(), 'exps_num_actual': expenses.filter(is_deleted=False).count(),
               "expen_num": expenses.count(), 'exp_rec_pie': exp_rec_pie, "pie_chart_year": pie_chart_year, 'user': request.user, 'suma': suma,
               'pie_chart_month': None}
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

    # Sklepy
    df_new = calculate_recurrent_expense(df_new)
    df_rec = pd.DataFrame(list(recs))
    df_rec.columns = ["receipt_name", "date_added", "amount",'shop']
    df_rec = calculate_date(df_rec)
    df_shops = pd.DataFrame(list(shops))
    df_shops.columns = ["shop", 'shop_name']
    df_rec = pd.merge(df_rec, df_shops, on=['shop'])

    df_new['shop'].fillna(Shop.objects.get(shop_name="Inne").id, inplace=True)
    df_new = pd.merge(df_new, df_shops, on=['shop'])
    df_rec = pd.concat([df_new, df_rec], axis=0)
    print(df_rec)
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


    df_rec = pd.concat([df_new, df_rec], axis=0)

    df_rec = df_rec[['shop_name', 'amount','date_added']]
    print(df_rec)
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

    context = {'rec_num': receipts.filter().count(),
               'rec_num_actual': receipts.filter(is_deleted=False).count(),
               'exps_num': expenses.filter().count(), 'exps_num_actual': expenses.filter(is_deleted=False).count(),
               "expen_num": expenses.count(), "exp_rec_pie": exp_rec_pie, 'user': request.user, 'suma': suma
               }
    return render(request, "statistics_and_plots/shops_charts.html", context)