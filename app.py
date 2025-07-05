from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def split_bill():
    result = None
    if request.method == 'POST':
        try:
            total = float(request.form['total'])
            people = int(request.form['people'])
            tip_percent = request.form['tip']

            tip = float(tip_percent) if tip_percent else 0
            tip_amount = (tip / 100) * total
            final_amount = total + tip_amount
            per_person = final_amount / people

            result = {
                'total': round(final_amount),
                'per_person': round(per_person)
            }
        except:
            result = {'error': 'لطفاً مقادیر معتبر وارد کنید.'}

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
