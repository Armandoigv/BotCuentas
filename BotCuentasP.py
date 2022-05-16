from config import * # Importamos el token
import telebot # Importaamos libreria pytelegrambotapi
import time
from telebot.types import ReplyKeyboardMarkup # Para crear botones
from telebot.types import ForceReply
import pandas as pd
from telebot.types import ReplyKeyboardRemove
import gspread
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from waitress import serve # Para ejecutar el servidor en un entorno de produccion
from flask import Flask, request # Para crear el servidor web (red domestica)

bot = telebot.TeleBot(TELEGRAM_TOKEN)
web_server = Flask(__name__)

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
cuentass = {}

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
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "En que se gasto?", reply_markup= markup)
    bot.register_next_step_handler(msg, monto)

def monto(message):
    """Cuanto se gasto?"""
    gastos[message.chat.id] = {}
    #gastos[message.date] = {}
    gastos[message.chat.id]['gasto'] = message.text
    #gastos[message.date]['gasto'] = message.text
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "Cuanto se gasto?", reply_markup= markup)
    bot.register_next_step_handler(msg, preguntar_banco_entrada)

def preguntar_banco_entrada(message):
    gastos[message.chat.id]['monto'] = message.text
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
    texto += f"Gasto:{gastos[message.chat.id]['gasto']}\n"
    texto += f"Monto:{gastos[message.chat.id]['monto']}\n"
    texto += f"Banco entrada:{gastos[message.chat.id]['banco_entrada']}\n"
    texto += f"Banco entrada:{gastos[message.chat.id]['banco_salida']}\n"

    # Cargar credenciales descargadas de tu cuenta gmail
    gc = gspread.service_account(filename= 'creds.json')
    # Cargar libro excel de google sheets
    sh = gc.open('CuentasAGV').sheet1
    sh.append_row([str(gastos[message.chat.id]['gasto']), str(gastos[message.chat.id]['monto']), str(gastos[message.chat.id]['banco_entrada']), str(gastos[message.chat.id]['banco_salida'])])
    markup = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, texto, parse_mode='html', reply_markup= markup)
    df = pd.DataFrame.from_dict(gastos)
    df.to_csv (r'gastos_telegram.csv', index = False, header=True)
    
@bot.message_handler(commands = ['TotalCuentas'])
def cmd_TotalCuentas(message):
    """En que se gasto"""
    # Cargar credenciales descargadas de tu cuenta gmail
    gc = gspread.service_account(filename= 'creds.json')
    # Cargar libro excel de google sheets
    sh = gc.open('CuentasAGV').sheet1
    diccionario  =  sh.get_all_records()
    df = pd.DataFrame(diccionario)
    Total = df['Monto'].sum()
    markup = ReplyKeyboardRemove()
    bot.reply_to(message, Total, reply_markup= markup)
    df.plot(kind="bar")
    plt.savefig('foo.png')
    bot.send_photo(message.chat.id, photo=open(r'C:\Users\INCOLUR\Mi unidad\08. Formación\Telegram\foo.png', 'rb'))
    

# Escritura de programa principal

# MAIN ##################

if __name__ == '__main__':
    print("Iniciando el bot")
    # Eliminamos el webhook
    bot.remove_webhook()
    # Pequeña pausa para que se elimine el webhook
    time.sleep(1)
    # Definimos el webhook
    bot.set_webhook(url= "https://botcuentas.herokuapp.com/")
    # arrancamos el servidor
    #web_server.run(host="0.0.0.0", port=5000)
    serve(web_server, host = '0.0.0.0', port =5000)

    # el codigo se detiene al instanciar el servidor

    
    # Ejecutamos un metodo del objeto bot que comprueba si se reciben mensajes nuevos
    #bot.infinity_polling()
