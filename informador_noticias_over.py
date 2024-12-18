from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pathlib import Path
import undetected_chromedriver as uc
import csv
from datetime import datetime
import os
#imports mail:
from dotenv import load_dotenv
from email.message import EmailMessage #creación del mensaje
import ssl #correo seguro
import smtplib  #envia el mail

#Primero cogemos el path completo de donde está el fichero ejecutable.
carpeta = Path('.')
paths = list(carpeta.glob('**/informador_noticias_over.exe'))
path_exe = os.path.abspath(str(paths[0]))

aplicacion_ruta = os.path.dirname(path_exe) #aquí se pone la ubicación del archivo ejecutable para crear el archivo csv en la misma carpeta
fecha_ahora = datetime.now()
dia_mes_ano = fecha_ahora.strftime("%d%m%Y")

def enviar_mail(links_tratados):
    try:
        load_dotenv() #pillamos entorno virtual y la pass que guardamos

        email_sender = "example@gmail.com"
        password = os.getenv("PASSWORD")
        #email_receiver = "example@gmail.com"
        email_receiver = "example@gmail.com"
        subject = "¡Nueva noticia en la página de Overwatch!"
        body = """
        ¡Hola! Parece que hay una nueva noticia en la página oficial de Overwatch, ve a comprobarlo en: https://overwatch.blizzard.com/es-es/news/. 
        ¡Aquí tienes los enlaces directos a las noticias!
        """
        for link in links_tratados:
            body = body+'\n- https://overwatch.blizzard.com/es-es{0}'.format(link)

        #creamos todo el mensaje que mandaremos con las variables creadas:
        email_msj = EmailMessage()
        email_msj["From"] = email_sender
        email_msj["To"] = email_receiver
        email_msj["Subject"] = subject
        email_msj.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context= context) as smtp: #servidor - puerto - contexto
            smtp.login(email_sender, password)
            smtp.sendmail(email_sender, email_receiver, email_msj.as_string()) #se envia el mail en formato string para poder ser leido
    except:
        print("Error: enviar_mail()")


def eliminar_archivo_anterior():
    try:
        diferentes = False
        directorio = Path("E:/github/python/informador_noticias_over/dist")
        lista = list(Path(directorio).glob('*.csv')) #Seleccionamos del path donde estamos todos los archivo que tengan .csv al final
        

        lista = sorted(lista, key=lambda file: Path(file).lstat().st_mtime) #con esta linea hacemos que se ordenen por tiempo de modificación, evitando que si es del año que viene con una fecha "inferior" borre el nuevo.

        if len(lista) > 1:
            with open(lista[0], 'r') as t1, open(lista[1], 'r') as t2:
                fileone = t1.readlines()
                filetwo = t2.readlines()

            for line in filetwo:
                    if line not in fileone:
                        diferentes = True

            if(diferentes == False):            
                lista[0].unlink()
                print("No hay diferencias, se borra el último archivo para que no haya problemas.")
                return False
            else:
                print("Hay diferencias.")
                lista[0].unlink()
                return True
            #retornamos true si se hay nueva noticia lo cual mandará correo, false si no hay nueva.
        return False
    except:
        print("Error: eliminar_archivo_anterior()")
        return False
        
def crear_fichero_noticias(): 
    try:
        website = "https://overwatch.blizzard.com/es-es/news/"
        path_driver = "E:/github/practicaAutomatizacion/automatisationPractise/informador_noticias_over/chrome_driver/chromedriver.exe"
        links_tratados = [] #los enlaces de aquí se guardaran para enviarlos por mail
        noticia_con_link = dict.fromkeys([0])
        
        driver_options = Options() #options cambia los valores por defecto sobre el navegador como tu elijas.
        driver_options.add_argument("--headless") #Headless mode (no se abre navegador, es "en segundo plano")
        
        driver_service = Service(executable_path=path_driver)
        driver_web = uc.Chrome(service=driver_service, options= driver_options)
        driver_web.get(website)
        news = driver_web.find_elements(by="xpath", value='//blz-card[@slot = "gallery-items"]')

        

        for index, new in enumerate(news):
            noticia_con_link[index]  = (new.get_attribute("href"), new.text)

            link_sin_tratar = str(noticia_con_link.get(index))#procesamos el link para que sea valido para enviarlo
            link_troceado = link_sin_tratar.split()
            links_tratados.append(link_troceado[0].replace("'", '').replace('(', '').replace(',', ''))
        
        #creación del archivo y rellenamos de valores para compararlo cada vez que se ejecute el programa
        nombre_archivo = f'noticias{dia_mes_ano}.csv' 
        ruta_final_archivo = os.path.join(aplicacion_ruta, nombre_archivo)

        with open(ruta_final_archivo, 'w') as fichero:
            escritor = csv.writer(fichero, noticia_con_link.keys())
            escritor.writerows(noticia_con_link.items())
        
        nueva_noticia = eliminar_archivo_anterior()

        if nueva_noticia:
            enviar_mail(links_tratados)
        else:
            print("No hay nuevas noticias.")
    except:
        print("¡Error!")
    finally:
        print("Cerrando drivers...")    
        driver_web.quit()
        
crear_fichero_noticias()