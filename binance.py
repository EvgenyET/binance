import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import numpy as np
import plotly.offline as pyo
import pandas as pd
import pickle
import webview

# ------------------------------------------------------------------------------------
'''Активируем данный блок, если нужно загрузить данные с Binance и сохранить их на диск:'''

# '''Загружаем данные Биткоина с биржи Binance:'''
#


# binance_client = Client(user_key, secret_key)
#
# binance_client.futures_symbol_ticker(symbol='BTCUSDT')
#
# binance_client.futures_historical_klines(
#     symbol='BTCUSDT',
#     interval='1d',  # can play with this e.g. '1h', '4h', '1w', etc.
#     start_str='2019-09-08',
#     end_str='2023-11-30'
# )
#
# df = pd.DataFrame(binance_client.futures_historical_klines(
#     symbol='BTCUSDT',
#     interval='1d',
#     start_str='2019-09-08',
#     end_str='2023-11-30'
# ))
#
# df.head()
#
# '''Сохраняем датафрейм BTC (с биржи Binance) на жесткий диск,
#  чтобы не грузить его постоянно из сети:'''
#
# with open('dataframe.pkl', 'wb') as file:
#     pickle.dump(df, file)

# ------------------------------------------------------------------------------------

'''Загружаем датафрейм Pandas из файла:'''

with open('dataframe.pkl', 'rb') as file:
    df = pickle.load(file)

'''Обрезаем ненужные столбцы из датафрейма:'''

df = df.iloc[:, :6]

'''Присваиваем имена столбцам:'''

df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

'''Преобразовываем временную метку в формат даты и убедимся, что все ohlcv имеют числовые значения:'''

df['Date'] = pd.to_datetime(df['Date'], unit='ms')
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col])
df.head()

'''Создаём MA200 и MA50:'''

df['ma200'] = df.Close.rolling(200).mean()
df['ma50'] = df.Close.rolling(50).mean()

'''Заполняем все пустые значения NaN MA200 и MA50 в датафрейме:'''

df['ma200'].bfill(inplace=True)
df['ma50'].bfill(inplace=True)

'''Пишем сигналы в Plotly (сначала убираем все индесы (нулевые значения), иначе возникает ошибка Key=0:'''

df.reset_index(inplace=True, drop=True)

df['Signal'] = None
previous_signal = None

for i in range(len(df)):
    if df.loc[i, 'Close'] < df.loc[i, 'ma200']:
        current_signal = 'Sell'
    else:
        current_signal = 'Buy'
    if current_signal != previous_signal:
        df.loc[i, 'Signal'] = current_signal
        previous_signal = current_signal

'''Добавляем новые колонки в таблицу (сопоставляем Sell и Buy с ценой закрытия Биткоина):'''

df["Sell_Price"] = np.where(df["Signal"] == "Sell", df["Close"], np.nan)
df["Buy_Price"] = np.where(df["Signal"] == "Buy", df["Close"], np.nan)

'''Выводим таблицу в консоль PyCharm:'''

print(df)
# df.to_csv('file2.csv')

# ------------------------------------------------------------------------------------

'''Добавляем свечной график BTC (и сразу убираем легенду для него):'''

fig = go.Figure()

fig.add_trace(go.Candlestick(x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                showlegend=False))

fig.update_layout(yaxis_type="log")

'''Накладываем на график MA200 и MA50:'''

fig.add_trace(go.Scatter(x=df['Date'], y=df['ma200'],mode='lines', line=dict(color='blue', width=1), name = 'ma200'))
fig.add_trace(go.Scatter(x=df['Date'], y=df['ma50'],mode='lines', line=dict(color='green', width=1), name = 'ma50'))

'''добавляем на график сигналы в виде синих и красных точек:'''

signal_sell = go.Scatter(
    x=df['Date'],  # x-coordinates of the signal points
    y=df['Sell_Price'],  # y-coordinates of the signal points
    mode='markers',
    name='Sell',
    text='<b>Sell</b>',
    hoverinfo='text',
    marker=dict(
        color='red',  # color of the signal points
        size=10  # size of the signal points
    )
)

signal_buy = go.Scatter(
    x=df['Date'],  # x-coordinates of the signal points
    y=df['Buy_Price'],  # y-coordinates of the signal points
    mode='markers',
    name='Buy',
    text='<b>Buy</b>',
    textfont=dict(size=20, color='red', family='Arial'),
    hoverinfo='text',
    marker=dict(
        color='blue',  # color of the signal points
        size=10  # size of the signal points
    )
)

'''Добавляем сигналы в виде точек на график:'''

fig.add_trace(signal_sell)
fig.add_trace(signal_buy)

'''Убираем нижний график rangeslider:'''

fig.update_layout(xaxis_rangeslider_visible=False)

# data = [go.Scatter(x=df['Date'], y=df['Close'])]
# fig = go.Figure(data=data, layout=go.Layout(
#     margin=dict(l=0)
# ))

'''меняем шаг сетки по оси x и оси y'''

fig.update_yaxes (tick0=0.07, dtick=0.07)
fig.update_xaxes(nticks=50)

'''округляем значения по оси x'''

fig.update_yaxes(tickformat=".0f")

'''делаем интерактивный курсор'''
#
fig.update_yaxes(spikecolor='darkgray', spikedash='dot', spikemode='across', spikesnap='cursor', spikethickness=1)
fig.update_xaxes(spikecolor='darkgray', spikedash='dot', spikemode='across', spikesnap='cursor', spikethickness=1)

'''изменяем цвет фона'''

fig.update_layout(plot_bgcolor='white')

'''изменяем цвет сетки'''

fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#F0F0F0')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#F0F0F0')

'''добавляем утолщение и цвет для оси x и оси y (а также зеркально дублируем (mirror=True))'''

fig.update_xaxes(showline=True, linewidth=2, linecolor='Silver', mirror=True)
fig.update_yaxes(showline=True, linewidth=2, linecolor='Silver', mirror=True)

'''форматируем дату'''

# fig.update_xaxes(tickformat="%B<br>%Y")

'''Убираем отступы на графике:
(в первом варианте устанавливаем максимально-минимальные начальные значения):'''

# fig.update_layout(
#     xaxis=dict(range=[df['Date'].min(), df['Date'].max()])
# )

fig.update_layout(
    xaxis=dict(range=['2019-09-01', df['Date'].max()])
)

'''Открыть график в браузере:'''

# fig.show()

'''Открыть график оффлайн в браузере:'''

# pyo.plot(fig, filename='chart.html')

'''Сохранить файл chart.html без автоматического открытия в браузере:'''

pyo.plot(fig, filename='chart.html', auto_open=False)

'''Импортируем переменную html из скрипта calculate_profit
и записываем кусок html-кода в конец цайла chart.html:'''

from calculate_profit import html

with open('chart.html', 'a', encoding='utf-8') as file:
    file.write(html)

'''Меняем заголовок в файле chart.html, чтобы поставить ссылку на стили css,
которые будут вписывать график вместе со статистикой в окно на 100%:'''

with open("chart.html", "r", encoding="utf-8") as file:
    # Read the contents of the file
    contents = file.readlines()

# Find the line you want to replace
for i, line in enumerate(contents):
    if '<head><meta charset="utf-8" /></head>' in line:
        # Replace the line with new_text
        contents[i] = line.replace('<head><meta charset="utf-8" /></head>',
                                   '<head><meta charset="utf-8" /><link rel="stylesheet" type="text/css" href="style.css"></head>')

with open("chart.html", "w", encoding="utf-8") as file:
    # Write the modified contents
    file.writelines(contents)

'''Открыть график как десктопное приложение на компьютере при помощи webview:'''

webview.create_window(title="График BTC", url="chart.html", width=1280, height=920, resizable=True)
webview.start(http_server=True)


