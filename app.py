from flask import Flask, render_template, request, redirect, session, make_response, clave_hash
from config.conexion import conexion
from fpdf import FPDF
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key="Miclave"
def mostrar_todo():
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM tbcliente")
    clientes = cursor.fetchall()
    cursor.close()
    return clientes

@app.route('/')
def index():
    if 'usuario' in session:
        clientes = mostrar_todo()
        mensaje = "Bienvenidos a la página de ventas"    
        return render_template('registrar.html', mensaje=mensaje, clientes=clientes)
    return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login():
    mensaje=''
    if request.method=='POST':
        user=request.form['txtuser']
        clave=request.form['txtclave']

        cursor=conexion.cursor()
        sql='Select * from tbusuario where user=%s AND clave =%s'
        cursor.execute(sql,(user,clave))
        usuario=cursor.fetchone()
        cursor.close()

        if usuario:
            session['usuario']=usuario[1]
            session['clave']=usuario[3]
            return redirect('/')
        else:
            mensaje="Usuario o contraseña incorrecto"
    return render_template('login.html',mensaje=mensaje)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/usuarios')
def usuarios ():
    return render_template('usuarios.html')

@app.route ('/insertar_usuarios', methods=['POST'])
def insertar_usuario ():
    user=request.form['txtuser']
    clave=request.form['txtclave']
    rol=request.form['txtrol']
    
    clave_hash=generate_password_hash(clave)
    cursor=conexion.cursor()
    sql="INSERT INTO tbusuario(user,clave,rol) VALUES(%s, %s, %s)"
    cursor.execute(sql,(user,clave_hash,rol))
    conexion.commit()
    cursor.close()

    return redirect('/logout')


@app.route('/reporte/<id>')
def generar_pdf(id):
    cursor = conexion.cursor()

    sql = """
    SELECT c.nombre, c.nit, co.producto, co.cantidad, co.costo
    FROM tbcompra co
    INNER JOIN tbcliente c ON co.tbcliente_ID_cliente = co.tbcliente_ID_cliente
    WHERE co.tbcliente_ID_cliente = %s
    """
    cursor.execute(sql, (id,))
    datos = cursor.fetchall()
    cursor.close()

    if not datos:
        return "No se encontraron compras para este cliente", 404

    nombre_cliente = datos[0][0]  # El nombre viene en la primera columna
    nit_cliente = datos[0][1]  # El NIT viene en la

    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="REPORTE DE COMPRAS", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Cliente: {nombre_cliente}", ln=True)
    pdf.cell(200, 5, txt=f"NIT: {nit_cliente}", ln=True)
    pdf.ln(5)

    # Cabecera de la tabla
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 10, "Producto", 1)
    pdf.cell(30, 10, "Cantidad", 1)
    pdf.cell(30, 10, "Costo", 1)
    pdf.cell(40, 10, "Total", 1)
    pdf.ln()

    # Datos
    pdf.set_font("Arial", '', 10)
    for fila in datos:
        _, _, producto, cantidad, costo = fila
        total = float(cantidad) * float(costo)
        pdf.cell(60, 10, str(producto), 1)
        pdf.cell(30, 10, str(cantidad), 1)
        pdf.cell(30, 10, f"{costo:.2f}", 1)
        pdf.cell(40, 10, f"{total:.2f}", 1)
        pdf.ln()

    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte_compras.pdf'
    return response

  

def mostrarCliente(id):
    cursor=conexion.cursor()
    sql="select * from tbcliente where ID_cliente=%s"
    cursor.execute(sql,(id,))
    datos=cursor.fetchone()
    return datos

@app.route('/comprar/<id>')
def comprar(id):
    datos=mostrarCliente(id)
    return render_template('comprar.html',id=id,datos=datos)


@app.route('/comprar', methods=['post'])
def insertarComprar():
    id=request.form['txtid']
    producto=request.form['txtproducto']
    cantidad=request.form['txtcantidad']
    costo=request.form['txtcosto']

    cursor=conexion.cursor()
    sql="INSERT INTO tbcompra (producto, cantidad,costo,tbcliente_ID_cliente) values(%s,%s,%s,%s)"
    cursor.execute(sql,(producto,cantidad,costo,id))
    conexion.commit()
    cursor.close
   
    return redirect('/')

@app.route('/vercompras/<id>',methods=['GET'])
def vercompras(id):
    cursor=conexion.cursor()
    sql="Select * from tbcompra where tbcliente_ID_cliente=%s"
    cursor.execute(sql,(id,))
    datos=cursor.fetchall()
    return render_template('vercompras.html',datos=datos)



@app.route('/insertar', methods=['POST'])
def insertar():
    nombre = request.form['txtnombre']
    nit = request.form['txtnit']
    cursor = conexion.cursor()
    sql = "INSERT INTO tbcliente(nombre, nit) VALUES (%s, %s)"
    cursor.execute(sql, (nombre, nit))
    conexion.commit()
    cursor.close()
    
    clientes = mostrar_todo()
    mensaje = "Registro insertado exitosamente"
    return render_template('registrar.html', mensaje=mensaje, clientes=clientes)

@app.route('/buscar', methods=['GET'])
def buscar():
    buscar=request.args.get('txtbuscar')
    cursor=conexion.cursor()
    sql="Select * from tbcliente where nombre LIKE %s"
    cursor.execute(sql,(buscar+'%',))
    mostrar=cursor.fetchone()
    return render_template('registrar.html',mostrar=mostrar)


@app.route('/actualizar/<id>')
def actualizar(id):
    cursor = conexion.cursor()
    sql = "SELECT * FROM tbcliente WHERE ID_cliente = %s"
    cursor.execute(sql, (id,))
    dato = cursor.fetchone()
    cursor.close()
    return render_template('actualizar.html', clientes=dato)

@app.route('/actualizar_ID_cliente', methods=['POST'])
def actualizar_cliente():
    id = request.form['txtid']
    nombre = request.form['txtnombre']
    nit = request.form['txtnit']
    cursor = conexion.cursor()
    sql = "UPDATE tbcliente SET nombre = %s, nit = %s WHERE ID_cliente = %s"
    cursor.execute(sql, (nombre, nit, id))
    conexion.commit()
    cursor.close()
    return redirect('/')

@app.route('/eliminar/<id>')
def eliminar(id):
    cursor = conexion.cursor()
    sql = "DELETE FROM tbcliente WHERE ID_cliente = %s"
    cursor.execute(sql, (id,))
    conexion.commit()
    cursor.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
