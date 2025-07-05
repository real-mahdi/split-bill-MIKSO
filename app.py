from flask import Flask, render_template, request, redirect, url_for
import uuid, os
import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta

app = Flask(__name__)
shared_data = {}

EXPIRATION_HOURS = 24

@app.route('/', methods=['GET', 'POST'])
def index():
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
                'created_at': datetime.now()
            }

            uid = str(uuid.uuid4())[:8]
            shared_data[uid] = result

            # Generate QR Code as base64
            link = request.host_url.rstrip('/') + url_for('shared', uid=uid)
            img = qrcode.make(link)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_img = base64.b64encode(buffered.getvalue()).decode()

            return render_template('share.html', result=result, uid=uid, qr_img=qr_img, link=link)

        except:
            return render_template('index.html', error='ورودی نامعتبر بود!')

    return render_template('index.html')

@app.route('/share/<uid>')
def shared(uid):
    data = shared_data.get(uid)
    if not data:
        return "این لینک پیدا نشد!"

    created = data.get('created_at')
    if not created or datetime.now() - created > timedelta(hours=EXPIRATION_HOURS):
        return "⏱️ این لینک منقضی شده است (بیش از ۲۴ ساعت گذشته)."

    return render_template('shared.html', result=data)

if __name__ == '__main__':
    app.run(debug=True)
