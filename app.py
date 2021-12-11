import uuid

from flask import Flask, render_template, request, redirect

app = Flask(__name__)

accounts = [
    {'id': uuid.uuid4().hex, 'username': 'test', 'password': 'test', 'amount': 1000},
    {'id': uuid.uuid4().hex, 'username': 'test1', 'password': 'test1', 'amount': 2000},
    {'id': uuid.uuid4().hex, 'username': 'test2', 'password': 'test2', 'amount': 3000},
    {'id': uuid.uuid4().hex, 'username': 'test3', 'password': 'test3', 'amount': 4000},
]
loans = []


@app.route('/')
def index():
    return render_template('index.html')


def add_loans_to_context(context, account):
    context['loans'] = loans
    total_loans = 0
    my_loan = None
    for i in loans:
        total_loans = total_loans + i['amount']
        if i['account']['id'] == account['id']:
            my_loan = i
    context['total_loans'] = total_loans
    context['my_loan'] = my_loan
    return context


@app.route('/home', methods=['GET', 'POST'])
def home():
    context = {
        'accounts': accounts,
        'loans': loans
    }
    uid = request.values.get('id')
    if uid is None:
        return redirect('/')
    account = None
    bulk_amount = 0
    for acc in accounts:
        if uid == acc['id']:
            account = acc
        bulk_amount = bulk_amount + acc['amount']
    if account is None:
        return redirect('/')
    context['account'] = account
    context['bulk_amount'] = bulk_amount
    form = request.values
    context = add_loans_to_context(context, account)
    if form.get('type') == 'pay':
        idx = 0
        for i in loans:
            if i['account']['id'] == uid:
                loans.pop(idx)
                break
            idx = idx + 1
        context = add_loans_to_context(context, account)
        return render_template('home.html', **context)
    if form.get('approved_person') is None:
        return render_template('home.html', **context)
    check_duplicate = False
    for i in loans:
        if i['account']['id'] == account['id']:
            check_duplicate = True
            break
    if check_duplicate:
        return render_template('home.html', **context)
    if form['approved_person'] == account['id']:
        if int(form['amount']) > account['amount']:
            context['error'] = 'Amount is high. Please select a approved person'
        else:
            loans.append({
                'id': uuid.uuid4().hex,
                'account': account,
                'amount': int(form.get('amount')),
                'approved_account': account
            })
    else:
        approved_account = None
        for i in accounts:
            if i['id'] == form.get('approved_person'):
                approved_account = i
                break
        if approved_account is None:
            context['error'] = 'Invalid approved person'
        else:
            for i in loans:
                if i['account']['id'] == approved_account['id']:
                    context['error'] = 'Approved person is on a loan. Please select a different approved person'
                    context = add_loans_to_context(context, account)
                    return render_template('home.html', **context)
            if int(form['amount']) > (account['amount'] + approved_account['amount']):
                context['error'] = 'Amount is high. Please select a different approved person'
            else:
                loans.append({
                    'id': uuid.uuid4().hex,
                    'account': account,
                    'amount': int(form.get('amount')),
                    'approved_account': approved_account
                })
    context = add_loans_to_context(context, account)
    return render_template('home.html', **context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = request.form
    for account in accounts:
        if form['username'] == account['username'] and form['password'] == account['password']:
            return redirect('/home?id=' + account['id'])
    context = {
        'error': 'Invalid username or password.'
    }
    return render_template('index.html', **context)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    context = {}
    form = request.form
    for account in accounts:
        if form['username'] == account['username']:
            context['error'] = 'Username already exists'
            return render_template('index.html', **context)
    if form['username'] is None:
        context['error'] = 'Invalid username'
        return render_template('index.html', **context)
    if form['password'] is None:
        context['error'] = 'Invalid password'
        return render_template('index.html', **context)
    if form['amount'] is None:
        context['error'] = 'Invalid amount'
        return render_template('index.html', **context)
    uid = uuid.uuid4().hex
    accounts.append({
        'id': uid,
        'username': form['username'],
        'password': form['password'],
        'amount': int(form['amount'])
    })
    return redirect('/home?id=' + uid)


if __name__ == '_main_':
    app.run(debug=True)