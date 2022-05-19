from config import * # Importamos el token
import telebot # Importaamos libreria pytelegrambotapi
import time
from telebot.types import ReplyKeyboardMarkup # Para crear botones
from telebot.types import ForceReply
import pandas as pd
from telebot.types import ReplyKeyboardRemove
from telebot.types import BotCommand
import gspread
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from waitress import serve # Para ejecutar el servidor en un entorno de produccion
from flask import Flask, request # Para crear el servidor web (red domestica)
import os 
import sys
import threading
from pandas.plotting import table 

bot = telebot.TeleBot(TELEGRAM_TOKEN)
web_server = Flask(__name__)

gc = gspread.service_account(filename= 'creds.json')
sh = gc.open('CuentasAGV').sheet1
sh2 = gc.open('CuentasAGV').get_worksheet(1)
diccionario  =  sh.get_all_records()
diccionario2  =  sh2.get_all_records()
df = pd.DataFrame(diccionario)
df2 = pd.DataFrame(diccionario2)

#hilo = threading.Thread(name = "hilo_web_server", target = arrancar_web_server)

#Gestiona las peticiones POST enviadas al servidor web
@web_server.route('/', methods = ['POST'])
def webhook():
    # Si el post recibido es un JSON
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200

gastos = {} # Crear diccionario

# responde al comando /start

# se debe utilizar decoradores. Empiezan por @ y luego el nombre de la funcion
# son funciones que reciben como parametro de entrada una funcion y devuelven otra funcion

@bot.message_handler(commands = ["start", "ayuda", "help"])

# Defir una funcion que por notacion empieza con cmd comando

def cmd_start(message):
    """Da la bienvenida al usuario del bot"""
    markup = ReplyKeyboardRemove()
    bot.reply_to(message, "Hola Armando, gtd", reply_markup= markup)
    #bot.send_message(message.chat.id, "Hola", parse_mode="html")


# Responder a comando /Cuentas

@bot.message_handler(commands = ['cuentas'])
def cmd_cuentas(message):
    """En que se gasto"""
    #print(datetime.date(message.date))
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "Hola!,En que se gastó?", reply_markup= markup)
    bot.register_next_step_handler(msg, monto)

def monto(message):
    """Cuanto se gasto?"""
    gastos[message.chat.id] = {}
    fecha = datetime.datetime.fromtimestamp(message.date)
    gastos[message.chat.id]['fecha'] = fecha
    gastos[message.chat.id]['gasto'] = message.text
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "Cuánto se gasto?", reply_markup= markup)
    bot.register_next_step_handler(msg, tipo)

def tipo(message):
    gastos[message.chat.id]['monto'] = int(message.text)
    markup = ReplyKeyboardMarkup(
            one_time_keyboard=True,
            input_field_placeholder="Pulsa un banco",
            resize_keyboard=True
            )
    markup.add("ENTRADA", "SALIDA")
    msg = bot.send_message(message.chat.id,"Que tipo de gasto es?", reply_markup= markup)
    bot.register_next_step_handler(msg, acumula)

def acumula(message):
    gastos[message.chat.id]['tipo'] = message.text
    markup = ReplyKeyboardMarkup(
            one_time_keyboard=True,
            input_field_placeholder="Pulsa un banco",
            resize_keyboard=True
            )
    markup.add("VERDADERO", "FALSO")
    msg = bot.send_message(message.chat.id,"Acumula puntos?", reply_markup= markup)
    bot.register_next_step_handler(msg, cargo)

def cargo(message):
    gastos[message.chat.id]['acumula'] = message.text
    markup = ReplyKeyboardMarkup(
            one_time_keyboard=True,
            input_field_placeholder="Pulsa un banco",
            resize_keyboard=True
            )
    markup.add("BICICLETA", "YO", "TRANSPORTE","OCIO","COMIDA","CUENTAS YO", "GREEMB", "MAMA")
    msg = bot.send_message(message.chat.id,"Tipo de Gasto?", reply_markup= markup)
    bot.register_next_step_handler(msg, preguntar_banco_entrada)

def preguntar_banco_entrada(message):
    gastos[message.chat.id]['cargo'] = message.text
    #gastos[message.date]['monto'] = message.text     
    markup = ReplyKeyboardMarkup(
            one_time_keyboard=True,
            input_field_placeholder="Pulsa un banco",
            resize_keyboard=True
            )
    markup.add("SCOT", "ITAU", "MPA", "MPD", "FPAYA", "FPAYD", "CHILEA","CHILED", "MACHA","MACHD","ACTIVOS","LIDERA", "CMR", "CHECKA","CHECKD")
    msg = bot.send_message(message.chat.id,"Desde que banco?", reply_markup= markup)
    bot.register_next_step_handler(msg, preguntar_banco_salida)

def preguntar_banco_salida(message):
    gastos[message.chat.id]['banco_entrada'] = message.text
    #gastos[message.date]['banco_entrada'] = message.text    
    markup = ReplyKeyboardMarkup(
            one_time_keyboard=True,
            input_field_placeholder="Pulsa un banco",
            resize_keyboard=True
            )
    markup.add("SCOT", "ITAU", "MPA", "MPD", "FPAYA", "FPAYD", "CHILEA","CHILED", "MACHA","MACHD","ACTIVOS","LIDERA", "CMR", "CHECKA","CHECKD")
    msg = bot.send_message(message.chat.id,"Hacia que banco?", reply_markup= markup)
    bot.register_next_step_handler(msg, guardar_datos_usuario)

def guardar_datos_usuario(message):
    gastos[message.chat.id]['banco_salida'] = message.text
    texto = 'Datos Introducidos\n' 
    texto += f"Gasto:{gastos[message.chat.id]['fecha']}\n"  
    texto += f"Gasto:{gastos[message.chat.id]['gasto']}\n"
    texto += f"Monto:{gastos[message.chat.id]['monto']}\n"
    texto += f"Monto:{gastos[message.chat.id]['tipo']}\n"
    texto += f"Monto:{gastos[message.chat.id]['acumula']}\n"
    texto += f"Monto:{gastos[message.chat.id]['cargo']}\n"
    texto += f"Banco entrada:{gastos[message.chat.id]['banco_entrada']}\n"
    texto += f"Banco entrada:{gastos[message.chat.id]['banco_salida']}\n"
    if gastos[message.chat.id]['cargo'] == "BICICLETA":
        sh.append_row(
        [str(gastos[message.chat.id]['gasto']),
        int(gastos[message.chat.id]['monto']),
        str(gastos[message.chat.id]['banco_entrada']),
        str(gastos[message.chat.id]['banco_salida']),
        str(gastos[message.chat.id]['fecha']),
        str(gastos[message.chat.id]['tipo']),
        str(gastos[message.chat.id]['acumula']),
        str(gastos[message.chat.id]['cargo'])]
        )
        sh.append_row(
        [str(gastos[message.chat.id]['gasto']),
        int(gastos[message.chat.id]['monto']*-1),
        str(gastos[message.chat.id]['banco_salida']),
        str(gastos[message.chat.id]['banco_entrada']),
        str(gastos[message.chat.id]['fecha']),
        str(gastos[message.chat.id]['tipo']),
        str(gastos[message.chat.id]['acumula']),
        str(gastos[message.chat.id]['cargo'])]
        )
    else:
        sh.append_row(
        [str(gastos[message.chat.id]['gasto']),
        int(gastos[message.chat.id]['monto']),
        str(gastos[message.chat.id]['banco_entrada']),
        str(gastos[message.chat.id]['banco_salida']),
        str(gastos[message.chat.id]['fecha']),
        str(gastos[message.chat.id]['tipo']),
        str(gastos[message.chat.id]['acumula']),
        str(gastos[message.chat.id]['cargo'])]
        )    
    markup = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, texto, parse_mode='html', reply_markup= markup)
   
@bot.message_handler(commands = ['totalcuentas'])
def cmd_totalcuentas(message):
    gc = gspread.service_account(filename= 'creds.json')
    sh = gc.open('CuentasAGV').sheet1
    sh2 = gc.open('CuentasAGV').get_worksheet(1)
    diccionario  =  sh.get_all_records()
    diccionario2  =  sh2.get_all_records()
    df = pd.DataFrame(diccionario)
    df2 = pd.DataFrame(diccionario2)
    table = pd.pivot_table(data=df,index=['Banco de entrada'])
    Total = df['Monto'].sum()
    fecha = datetime.datetime.fromtimestamp(message.date)
    sh2.append_row([str(fecha),int(Total)])
    markup = ReplyKeyboardRemove()
    bot.reply_to(message,"${:,.1f}".format(Total), reply_markup= markup)
    #dfSCOT = df[df['Banco de entrada'] == "SCOT"] 
    #dfSCOT.plot(x ='Banco de entrada', y='Monto',kind="bar")
    table.plot(kind="bar")
    #.yaxis.set_major_formatter('${x:1.2f}')
    plt.tight_layout()
    plt.savefig('imoo.png')
    df2.plot(x="Fecha",kind="line")
    plt.xticks(rotation=270)
    plt.tight_layout()
    plt.savefig('imoos.png')
    bot.send_photo(message.chat.id, photo=open('imoo.png', 'rb'))
    bot.send_photo(message.chat.id, photo=open('imoos.png', 'rb'))
    #bot.send_photo(message.chat.id, photo=plt.show())
    

@bot.message_handler(commands = ['cuentastabla'])
def cmd_cuentastabla(message):
    table = pd.pivot_table(data=df,index=['Banco de entrada'],values = ['Monto'])
    texto = 'Datos Introducidos\n'
    for count,ele in enumerate(table['Monto']):
        a ="${:,.1f}".format(ele)
        b=""
        c=len(max(list(table.index), key=len))-len(table.index[count])+1
        texto += f"B:{table.index[count]}"+ b.ljust(c)+f"<u>M: {a}</u>\n"  
    markup = ReplyKeyboardRemove()
    texto = "<pre>"+texto+"</pre>"
    bot.send_message(message.chat.id, texto, parse_mode='html', reply_markup= markup)
  
@bot.message_handler(commands = ['cuentashtml'])
def cmd_cuentashtml(message):
    tabla2 = df[df['Banco de entrada'] =="SCOT"][["Fecha"]]
    texto = 'Datos Introducidos\n'
    for count,ele in enumerate(tabla2['Monto']):
        a ="${:,.1f}".format(ele)
        b=""
        c=len(max(list(tabla2.index), key=len))-len(tabla2.index[count])+1
        texto += f"B:{tabla2[count]}"+ b.ljust(c)+f"<u>M: {a}</u>\n"  
    markup = ReplyKeyboardRemove()
    texto = "<pre>"+texto+"</pre>"
    markup = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, texto, parse_mode='html', reply_markup= markup)

@bot.message_handler(commands = ['cuentasbip'])
def cmd_cuentasbip(message):
    #testo.split()
    #testo.split()[1:]
    #" ".join(testo.split()[1:])
    monto = " ".join(message.text.split()[1:])
    # Si no se han pasado parametros
    if not monto:
        texto = "Debes introducir una busqueda.\n"
        texto+= "Ejemplo:\n"
        texto+= f'<code>{message.text} hola mundo </code>'
        bot.send_message(message.chat.id, texto,parse_mode="html")
        return 1
    else:
        fecha = datetime.datetime.fromtimestamp(message.date)
        print(fecha)
        sh.append_row(["BIP",int(monto),"CMR","GASTO",str(fecha),"CMR","VERDADERO","TRANSPORTE"])
        texto = "Transporte añadido"
        markup = ReplyKeyboardRemove()
        bot.send_message(message.chat.id, texto, parse_mode='html', reply_markup= markup)




# Escritura de programa principal

def polling():
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()

def arrancar_web_server():
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url= 'https://botcuentas.herokuapp.com/')
    serve(web_server, host = '0.0.0.0', port = int(os.environ.get('PORT',5000)))

# MAIN ##################

if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand('/start', 'Inicio del bot'),
        telebot.types.BotCommand('/cuentas', 'Añade gasto o ingreso'),
        telebot.types.BotCommand('/totalcuentas', 'Balance total'),
        telebot.types.BotCommand('/cuentastabla', 'Balance por banco'),
        telebot.types.BotCommand('/cuentashtml', 'Detalle por Banco'),
        telebot.types.BotCommand('/cuentasbip', 'Añade gasto frecuente')
        ])
    print("Iniciando el bot")
    if os.environ.get("DYNO_RAM"):
        hilo = threading.Thread(name = "hilo_web_server", target = arrancar_web_server)
        #pass #iniciamos el servidor web
    else:
        hilo = threading.Thread(name = "hilo_polling", target = polling)
    
    # Iniciamos el hilo que corresponda
    hilo.start()

