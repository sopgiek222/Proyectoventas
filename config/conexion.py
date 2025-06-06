import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="root", 
    password="1234", 
    database="bdventas")

cursor=conexion

