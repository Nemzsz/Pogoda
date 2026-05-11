import requests
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
import os

ramka_pogody = None
zatemnitel = None
nadpis_zagruzki = None
fon_izobrazhenie = None

def zagruzit_fon(put_k_faylu, shirina, vysota):
    if os.path.exists(put_k_faylu):
        try:
            izobrazhenie = Image.open(put_k_faylu)
            izobrazhenie = izobrazhenie.resize((shirina, vysota), Image.LANCZOS)
            return ImageTk.PhotoImage(izobrazhenie)
        except Exception as oshibka:
            print(f"Ошибка загрузки фона: {oshibka}")
    return None

def poluchit_dannye():
    ssylka = "https://wttr.in/Moscow?format=j1"  #отдает джсон

    try:
        otvet = requests.get(ssylka, timeout=15)
        otvet.raise_for_status()
        return otvet.json()  #в словарь
    except:
        pass

    #для запаса
    try:
        ssylka_zapas = "https://api.open-meteo.com/v1/forecast"
        parametry = {
            "latitude": 55.7558,
            "longitude": 37.6173,
            "current_weather": True,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode",  #для дней
            "timezone": "Europe/Moscow",
            "forecast_days": 5
        }

        otvet = requests.get(ssylka_zapas, params=parametry, timeout=15)
        otvet.raise_for_status()
        dannye_raw = otvet.json()  #полученным джсон
        tekushaya = dannye_raw['current_weather']  #сама погода
        dannye = {
            'current_condition': [{
                'temp_C': str(tekushaya['temperature']),
                'FeelsLikeC': str(round(tekushaya['temperature'] - 2, 1)),
                'windspeedKmph': str(int(tekushaya['windspeed'] * 1.6)),
                'weatherDesc': [{'value': pogoda_po_kodu(tekushaya['weathercode'])}]
            }], 'weather': []
        }

        #для 5 днйе
        for i in range(5):
            den = {
                'date': dannye_raw['daily']['time'][i],
                'maxtempC': str(dannye_raw['daily']['temperature_2m_max'][i]),
                'mintempC': str(dannye_raw['daily']['temperature_2m_min'][i]),
                'hourly': [{'time': '1200',
                            'weatherDesc': [{'value': pogoda_po_kodu(dannye_raw['daily']['weathercode'][i])}],  #!!код!!
                            'tempC': str(dannye_raw['daily']['temperature_2m_max'][i]),
                            'windspeedKmph': '—',
                            'humidity': '—'}]
            }
            dannye['weather'].append(den)
        return dannye  #возвращеение словаря

    except Exception as oshibka:
        messagebox.showerror("Ошибка", "Не удалось получить данные о погоде.\n\n" "Проверьте подключение к интернету\n"
                             "и попробуйте ещё раз.\n\n"
                             f"Ошибка: {oshibka}")
        return None
def pogoda_po_kodu(kod):
    kody = {
        0: "Ясно ☀️",
        1: "Преимущественно ясно 🌤️",
        2: "Переменная облачность ⛅",
        3: "Пасмурно ☁️",
        45: "Туман 🌫️",
        48: "Изморозь 🌫️",
        51: "Морось 🌧️",
        53: "Морось 🌧️",
        55: "Морось 🌧️",
        61: "Дождь 🌧️",
        63: "Дождь 🌧️",
        65: "Сильный дождь 🌧️",
        71: "Снег ❄️",
        73: "Снег ❄️",
        75: "Сильный снег ❄️",
        77: "Снежные зёрна ❄️",
        80: "Ливень ⛈️",
        81: "Ливень ⛈️",
        82: "Сильный ливень ⛈️",
        85: "Снегопад 🌨️",
        86: "Сильный снегопад 🌨️",
        95: "Гроза ⛈️",
        96: "Гроза с градом ⛈️",
        99: "Сильная гроза ⛈️"
    }
    return kody.get(kod, "—")

def pokazat_pogodu(okno):
    global ramka_pogody, zatemnitel, nadpis_zagruzki
    if ramka_pogody is not None:
        try:
            zatemnitel.destroy()
            ramka_pogody.destroy()
        except:
            pass
        ramka_pogody = None
        zatemnitel = None
        return
    nadpis_zagruzki = tk.Label(okno, text="Подождите, информация грузится!", font=("Arial", 12), fg="#FF6F00")
    nadpis_zagruzki.place(relx=0.5, rely=0.9, anchor="center")
    okno.update()
    dannye = poluchit_dannye()  #!!!парсингНеТрогать!!!
    if nadpis_zagruzki:
        nadpis_zagruzki.destroy()
        nadpis_zagruzki = None

    if not dannye:
        return

    zatemnitel = tk.Frame(okno, bg="black")
    zatemnitel.place(relwidth=1, relheight=1)
    ramka_pogody = tk.Frame(okno)
    ramka_pogody.place(relx=0.5, rely=0.5, anchor="center", width=800, height=600)
    fon_pogody = zagruzit_fon("Fon.jpg", 800, 600)
    if fon_pogody:
        fon_label_pogody = tk.Label(ramka_pogody, image=fon_pogody)
        fon_label_pogody.image = fon_pogody
        fon_label_pogody.place(x=0, y=0, relwidth=1, relheight=1)

    def zakryt():
        global ramka_pogody, zatemnitel
        zatemnitel.destroy()
        ramka_pogody.destroy()
        ramka_pogody = None
        zatemnitel = None

    knopka_zakryt = tk.Button(ramka_pogody, text="✕", font=("Arial", 14, "bold"), bg="#FF6F00", fg="white", relief="flat",
        bd=0, cursor="hand2", command=zakryt)
    knopka_zakryt.place(relx=0.97, rely=0.02, anchor="ne")
    tekushaya = dannye['current_condition'][0]  #из парсинга тащит, тоже не трогать

    tk.Label(ramka_pogody, text="Москва", font=("Arial", 14, "bold"),fg="#333").place(relx=0.5, rely=0.1, anchor="center")

    tk.Label(ramka_pogody, text=f"{tekushaya['temp_C']}°C", font=("Arial", 58, "bold"),fg="#FF6F00").place(relx=0.5, rely=0.22, anchor="center")

    try:
        oshchushchaetsya = round(float(tekushaya['FeelsLikeC']), 1)
    except:
        oshchushchaetsya = tekushaya['FeelsLikeC']

    tk.Label(ramka_pogody, text=f"Ощущается как {oshchushchaetsya}°C", font=("Arial", 12), fg="#555").place(relx=0.5, rely=0.3, anchor="center")
    tk.Label(ramka_pogody, text=tekushaya['weatherDesc'][0]['value'], font=("Arial", 13, "bold"), fg="#FF6F00").place(relx=0.5, rely=0.36, anchor="center")
    ramka_veter = tk.Frame(ramka_pogody, bg="#FFF3E0")
    ramka_veter.place(relx=0.5, rely=0.44, anchor="center")

    tk.Label(ramka_veter, text="💨 Ветер", font=("Arial", 13), bg="#FFF3E0").pack(padx=25, pady=(8, 0))
    tk.Label(ramka_veter, text=f"{tekushaya['windspeedKmph']} км/ч", font=("Arial", 14, "bold"), bg="#FFF3E0",fg="#E65100"
    ).pack(padx=25, pady=(0, 8))
    tk.Frame(ramka_pogody, bg="#FF8C00", height=2, width=300).place(relx=0.5, rely=0.53, anchor="center")

    tk.Label(ramka_pogody, text="Прогноз на 5 дней", font=("Arial", 14, "bold"), fg="#333").place(relx=0.5, rely=0.58, anchor="center")

    ramka_dni = tk.Frame(ramka_pogody)
    ramka_dni.place(relx=0.5, rely=0.8, anchor="center", width=600, height=200)

    dni_nedeli_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    mesiatsy_ru = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]

    #сортировка по критериям
    for nomer, prognoz in enumerate(dannye['weather'][:5]):  #джс
        data = prognoz['date']
        data_obj = datetime.strptime(data, "%Y-%m-%d")  #строка
        den = dni_nedeli_ru[data_obj.weekday()]
        mesyats = mesiatsy_ru[data_obj.month - 1]
        data_korotko = f"{den} {data_obj.day} {mesyats}"

        if nomer == 0:
            tsvet_fona = "#FFF3E0"
            tsvet_teksta = "#E65100"
            shrift = ("Arial", 11, "bold")
        else:
            tsvet_fona = "#FAFAFA"
            tsvet_teksta = "#333"
            shrift = ("Arial", 11)

        ramka_dnya = tk.Frame(ramka_dni, bg=tsvet_fona)
        ramka_dnya.pack(fill="x", pady=1, ipady=3)

        ramka_stroka = tk.Frame(ramka_dnya, bg=tsvet_fona)
        ramka_stroka.pack(fill="x", padx=10, pady=3)

        tk.Label(ramka_stroka, text=data_korotko, font=shrift, bg=tsvet_fona, fg=tsvet_teksta, width=14, anchor="w").pack(side="left")

        tk.Label(ramka_stroka, text=f"↑{prognoz['maxtempC']}°  ↓{prognoz['mintempC']}°", font=shrift, bg=tsvet_fona, fg=tsvet_teksta
        ).pack(side="left", padx=15)

        opisanie_dnya = ""
        for chast in prognoz['hourly']:  #для часов
            if int(chast['time']) == 1200:
                opisanie_dnya = chast['weatherDesc'][0]['value']
                break

        if not opisanie_dnya and prognoz['hourly']:
            opisanie_dnya = prognoz['hourly'][0]['weatherDesc'][0]['value']  #еслине12

        if opisanie_dnya:
            tk.Label(
                ramka_stroka,
                text=opisanie_dnya,
                font=("Arial", 10),
                bg=tsvet_fona,
                fg="gray"
            ).pack(side="right")


def sozdat_okno():
    okno = tk.Tk()
    okno.title("Погода Москва")
    okno.geometry("800x600")
    okno.resizable(False, False)

    global fon_izobrazhenie
    fon_izobrazhenie = zagruzit_fon("Fon.jpg", 800, 600)

    if fon_izobrazhenie:
        fon_label = tk.Label(okno, image=fon_izobrazhenie)
        fon_label.place(x=0, y=0, relwidth=1, relheight=1)
    else:
        okno.configure(bg="#87CEEB")

    put_k_solntsu = "kn.jpg"
    knopka_solntse = None

    if os.path.exists(put_k_solntsu):
        try:
            izobrazhenie_solntse = Image.open(put_k_solntsu)
            izobrazhenie_solntse = izobrazhenie_solntse.resize((220, 220), Image.LANCZOS)
            foto_solntsa = ImageTk.PhotoImage(izobrazhenie_solntse)

            knopka_solntse = tk.Label(okno, image=foto_solntsa, cursor="hand2")
            knopka_solntse.image = foto_solntsa
            knopka_solntse.place(relx=0.5, rely=0.45, anchor="center")
        except Exception as oshibka:
            print(f"Ошибка загрузки kn.jpg: {oshibka}")

    if not knopka_solntse:
        knopka_solntse = tk.Label(
            okno,
            text="☀️",
            font=("Arial", 80),
            cursor="hand2"
        )
        knopka_solntse.place(relx=0.5, rely=0.45, anchor="center")

    knopka_solntse.bind("<Button-1>", lambda e: pokazat_pogodu(okno))

    tk.Label(okno, text="Нажми на солнце", font=("Arial", 12), fg="#555").place(relx=0.5, rely=0.7, anchor="center")
    return okno
if __name__ == "__main__":
    okno = sozdat_okno()
    okno.mainloop()