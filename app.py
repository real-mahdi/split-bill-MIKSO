from flask import Flask, render_template, request
import datetime

app = Flask(__name__)
history = []

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        names = request.form.getlist('name')
        amounts = request.form.getlist('amount')

        try:
            people = []
            total_paid = 0

            for i in range(len(names)):
                name = names[i].strip()
                amount = float(amounts[i])
                people.append({'name': name, 'paid': amount})
                total_paid += amount

            average = total_paid / len(people)
            for person in people:
                person['diff'] = round(person['paid'] - average, 2)

            debtors = [p for p in people if p['diff'] < 0]
            creditors = [p for p in people if p['diff'] > 0]

            transactions = []
            i, j = 0, 0
            while i < len(debtors) and j < len(creditors):
                debtor = debtors[i]
                creditor = creditors[j]
                owed = min(abs(debtor['diff']), creditor['diff'])

                transactions.append({
                    'from': debtor['name'],
                    'to': creditor['name'],
                    'amount': round(owed, 2)
                })

                debtor['diff'] += owed
                creditor['diff'] -= owed

                if abs(debtor['diff']) < 0.01:
                    i += 1
                if creditor['diff'] < 0.01:
                    j += 1

            result = {
                'people': people,
                'transactions': transactions,
                'total': round(total_paid, 2),
                'average': round(average, 2),
                'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Add to history
            history.append(result)

        except:
            result = {'error': 'خطا در ورودی‌ها. لطفاً فقط عدد وارد کنید.'}

    return render_template('index.html', result=result)

@app.route('/history')
def view_history():
    return render_template('history.html', history=history)

if __name__ == '__main__':
    app.run(debug=True)
