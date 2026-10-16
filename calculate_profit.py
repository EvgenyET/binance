import webview

deposit = 100
leverage = 5
pnl = 2
sdelki = 3
time = 4
profit = 220

html = f"""
  <html>
    <body>
      <div style="padding-left:60px;">
      <h1 id="heading"><font face="Arial"><p><font size="5">Статистика сделок:</p></h1>
      <div class="content"><font size="3">Депозит: {deposit} Usdt</div>
      <div class="content">Плечо: x{leverage}</div>
      <div class="content">Прибыль: {pnl}%</div>
      <div class="content">Количество сделок: {sdelki}</div>
      <div class="content">Время в сделке: {time} дней</div>
      <div class="content">Общая прибыль: {profit} Usdt</div>
    </body>
  </html>
"""

def get_elements(window):
    heading = window.get_elements('#heading')
    content = window.get_elements('.content')

if __name__ == '__main__':
    window = webview.create_window('Статистика сделок', html=html, width=300, height=300, resizable=True)
    webview.start(get_elements, window)