from flask import Flask, render_template

app = Flask(__name__)

@app.route('/modern_india_2025')
def forum():
    
    return render_template('forums.html')

@app.route('/operation_sindoor')
def forum2():
    
    return render_template('forums2.html')

@app.route('/forum3')
def forum3():
    
    return render_template('forums3.html')

@app.route('/forum4')
def forum4():
    
    return render_template('forums4.html')

@app.route('/pk_wizard')
def pk_wizard():
    
    return render_template('pk_wizard.html')

@app.route('/ui_enthusiast')
def ui_enthusiast():
    
    return render_template('ui_enthusiast.html')

@app.route('/deligent_fly')
def deligent_fly():
    
    return render_template('deligent_fly.html')

@app.route('/crock')
def crock():
    
    return render_template('crock.html')

@app.route('/Clear_Raspberry')
def Clear_Raspberry():
    
    return render_template('Clear_Raspberry.html')

if __name__ == "__main__":
    app.run('0.0.0.0',debug=True, port=8080)
