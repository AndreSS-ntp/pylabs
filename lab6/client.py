import tkinter as tk
from tkinter import ttk, messagebox
from urllib import request, error
import json

SERVER_URL='http://0.0.0.0:8099/process'

class ClientApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Клиент — обработка текста (ЛР)')
        self.geometry('900x500')
        self.minsize(800,450)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(4, weight=1)

        ttk.Label(self, text='Введите текст:', padding=(10,10,10,0)).grid(row=0,column=0,sticky='w')
        self.input = tk.Text(self, height=10, wrap='word')
        self.input.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0,6))

        bar = ttk.Frame(self); bar.grid(row=2, column=0, sticky='ew', padx=10)
        ttk.Button(bar, text='Отправить на сервер', command=self.process).pack(side='right')

        ttk.Label(self, text='Результат:', padding=(10,10,10,0)).grid(row=3,column=0,sticky='w')
        self.output = tk.Text(self, height=10, wrap='word')
        self.output.grid(row=4, column=0, sticky='nsew', padx=10, pady=(0,10))

        hint = ('Правила обработки:\n'
                '— перед запятой пробелов быть не может;\n'
                '— после запятой ровно один пробел;\n'
                '— запрещены подряд две запятые;\n'
                '— текст не может начинаться с запятой.')
        ttk.Label(self, text=hint, padding=(10,0,10,10)).grid(row=5, column=0, sticky='w')

    def process(self):
        text = self.input.get('1.0','end-1c')
        try:
            data = json.dumps({'text': text}, ensure_ascii=False).encode('utf-8')
            req = request.Request(SERVER_URL, data=data, headers={'Content-Type':'application/json; charset=utf-8'})
            with request.urlopen(req, timeout=5) as resp:
                payload = json.loads(resp.read().decode('utf-8'))
            self.output.delete('1.0','end')
            self.output.insert('1.0', payload.get('text',''))
        except error.URLError as e:
            messagebox.showerror('Ошибка соединения', f'Не удалось связаться с сервером.\n{e}')
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))

def main():
    app = ClientApp()
    app.mainloop()

if __name__=='__main__':
    main()
