import urllib.parse
from urllib.parse import unquote
import stripe
import os
from os import path, environ
from app import app
from flask import render_template, request, redirect, make_response, jsonify
from app.emailer import Email
from app.worder import WordDoc
from app import letter_script
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.flaskenv'))

stripe_keys = {
    "secret_key": environ.get("STRIPE_SECRET_KEY"),
    "publishable_key": environ.get("STRIPE_PUBLISHABLE_KEY"),
    "endpoint_secret": environ.get("STRIPE_ENDPOINT_SECRET"),
}

stripe.api_key = stripe_keys["secret_key"]


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", title='Write My Rights')

# add the json router 
@app.route('/examplequestions')
def example1():
    # set path o read the local files, but we should upload files though web instead.
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    # json_url = os.path.join(SITE_ROOT, "static/", "form-simple.json")
    json_url = os.path.join(SITE_ROOT, "static/", "employmentLayoffTemplate.json")
    data = json.load(open(json_url))
    # connecting to the temporate folder
    return render_template("questionExample.html", data=data)

# add the json router with object constructor have not done the post yet
@app.route('/examplequestionsobject', methods=['GET', 'POST'])
def example2():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/", "form-simple-2.json")
    data = json.load(open(json_url))

    return render_template("questionExampleObjectTest.html", data=data)

# add the json router with object constructor have not done the post yet
@app.route('/cellphone', methods=['GET', 'POST'])
def cellphoneRoute():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/", "cellphoneComplaintTemplate.json")
    data = json.load(open(json_url))
    return render_template("questionCellphone.html", data=data)


# success submit the form
@app.route("/success", methods=['GET', 'POST'])
def success():
    if request.method == 'POST':
        print(request.form)
        return "recieved the data"

@app.route('/termsOfService')
def termsOfService():
    return render_template("termsOfService.html")

@app.route('/privacyPolicy')
def privacyPolicy():
    return render_template("privacyPolicy.html")

@app.route('/letterType')
def write_my_rights_info():
    return render_template("/letterType.html", title="Write My Rights Letter Type")


@app.route('/questions/<template>/<question>')
def question(template, question):
    return render_template("questions/"+template+"/"+question+".html", title=question)

@app.route('/questions/letterPreview')
def letterPreview():
    return render_template("questions/letterPreview.html", title="letterPreview")

@app.route('/questions/fetchLetter')
def fetchLetter():
    return render_template("/questions/fetchLetter.html", title="fetchLetter")

@app.route('/paymentDone')
def paymentDone():
    Email(request.cookies.get('email'), request.cookies.get('name') + ".docx").send()
    return render_template("/paymentDone.html", title="Payment Done")

@app.route('/paymentOption')
def paymentOption():
    return render_template("/paymentOption.html", title="Payment Option")

@app.route('/paymentTable')
def paymentTable():
    return render_template("/paymentTable.html", title="Payment Table")

@app.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)


@app.route("/create-checkout-session")
def create_checkout_session():
    domain_url = "http://localhost:5000/"
    stripe.api_key = stripe_keys["secret_key"]

    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - capture the payment later
        # [customer_email] - prefill the email input in the form
        # For full details see https://stripe.com/docs/api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "questions/fetchLetter",
            cancel_url=domain_url + "paymentOption",
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "name": "lettertest",
                    "quantity": 1,
                    "currency": "cad",
                    "amount": "100",
                }
            ]
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )

    except ValueError as e:
        # Invalid payload
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return "Invalid signature", 400

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        print("Payment was successful.")
        # TODO: run some custom code here

    return "Success", 200


@app.route('/answer', methods=['GET', 'POST'])
def answer():
    error = ''
    try:
        if request.method == 'POST':

            key = request.form['key']

            # single answers
            if 'answer' in request.form:
                attempted_value = request.form['answer']

            # multi answers up to 10
            else:
                attempted_value = dict()
                # if name for input = answer(1 - 10) this will store it all within a json object string before setting as a cookie
                for i in range(9):
                    if 'answer' + str(1 + i) not in request.form:
                        break
                    else:
                        print(request.form['answer' + str(1+i)])
                        attempted_value['a' + str(1+i)] = request.form['answer' + str(1+i)]
                # attempted_value = json.dumps(attempted_value)

            next_page = request.form['next_page']
            letter_type = request.form['letter_type']
            res = make_response(redirect('/questions' + letter_type + next_page))

            if type(attempted_value) == str or type(attempted_value) == dict:
                if key == 'bossName':
                    if attempted_value == '':
                        attempted_value = 'Sir or Madam'
                if key == 'email':
                    if attempted_value['a1'] == attempted_value['a2']:
                        attempted_value = attempted_value['a1']
                    else:
                        res = make_response(redirect('/questions/question16'))
                        res.set_cookie(key, 'Emails do not match', max_age=1)
                        return res
                if key == 'severance':
                    try:
                        if attempted_value['a2'] == 'on' or attempted_value['a1'] == '':
                            attempted_value = '0'
                        else:
                            attempted_value = attempted_value['a1']
                    except:
                        try:
                            if attempted_value['a1'] == '':
                                attempted_value = '0'
                            else:
                                attempted_value = attempted_value['a1']
                        except:
                            attempted_value = '0'
                print(urllib.parse.quote(attempted_value))
                attempted_value = urllib.parse.quote(attempted_value)
                res.set_cookie(key, attempted_value, max_age=3600)
                return res
            else:
                error = "Invalid Answer"

        return error, 401
    except Exception as e:
        print(e)
        return error, 402


def month_delta(start_date, end_date):
    delta = relativedelta(end_date, start_date)
    return 12 * delta.years + delta.months


@app.route('/questions/employment/getAnswers')
def getAnswers():
    print("start")
    ans = {}
    # client name
    ans['name'] = unquote(request.cookies.get('name'))
    # client home address
    ans['personal_address'] = unquote(request.cookies.get('personalAddress'))
    # client email
    ans['email'] = unquote(request.cookies.get('email'))
    # company name
    ans['company_name'] = unquote(request.cookies.get('company'))
    # company's address
    ans['company_address'] = unquote(request.cookies.get('employerAddress'))
    # client job title
    ans['job_title'] = unquote(request.cookies.get('jobTitle'))
    # length of time to find a job
    ans['findJobLength'] = unquote(request.cookies.get('findJobLength'))
    # Amount of job experience
    ans['experience'] = unquote(request.cookies.get('experience'))
    # company boss' name
    ans['boss_name'] = unquote(request.cookies.get('bossName'))
    # reason for layoff
    # ans['reason'] = unquote(request.cookies.get('reason'))
    # severance paid (in weeks/months)
    ans['severance_paid'] = unquote(request.cookies.get('severance'))
    # severance Demand
    ans['severance_demand'] = unquote(request.cookies.get('severanceDemand'))
    # vacation pay
    ans['vacation'] = unquote(request.cookies.get('vacation'))
    # client's mood (determines the letter template)
    ans['mood'] = unquote(request.cookies.get('mood'))

    # written apology
    ans['apology'] = unquote(request.cookies.get('apology'))
    # time worked at the company
    date_hired = datetime.strptime(request.cookies.get('hire_date'), '%Y-%m-%d')
    date_fired = datetime.strptime(request.cookies.get('fireDate'), '%Y-%m-%d')
    total_months_worked = (month_delta(date_hired, date_fired))
    ans['years_worked'] = int(total_months_worked/12)
    ans['months_worked'] = int((total_months_worked/12 % 1) * 12)

    # today's date
    ans['date'] = datetime.today().strftime("%B %d, %Y")
    # job start date
    ans['job_start_date'] = date_hired.strftime("%B %d, %Y")
    # Date of layoff
    ans['fire_date'] = date_fired.strftime("%B %d, %Y")
    # response date
    ans['response_date'] = datetime.strptime(request.cookies.get('deadline'), '%Y-%m-%d').strftime("%B %d, %Y")
    # written apology
    ans['apology'] = request.cookies.get('apology')

    letter = letter_script.create_employment_letter_preview(ans)
    sent_letter = letter_script.create_employment_letter(ans)
    WordDoc(sent_letter, ans).create()
    res = make_response(redirect('/questions/letterPreview'))
    letter = urllib.parse.quote(letter)
    res.set_cookie('written_letter', letter)

    return res



