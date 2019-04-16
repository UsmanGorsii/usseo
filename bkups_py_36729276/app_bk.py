import datetime
from flask import Flask, flash, render_template, request, session
from modules import dbapi
from modules import main
import os

app = Flask(__name__)
app.secret_key = os.urandom(12)
db = dbapi.dbapius()
username = db.getusername()[0]
password = db.getusername()[1]


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ip = request.environ['REMOTE_ADDR']
        else:
            ip = request.environ['HTTP_X_FORWARDED_FOR']
        notupdatedstats = db.getstats()
        db.updatelogin(datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y'), ip)
        return render_template("dash.html", stats=notupdatedstats)


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == password and request.form['username'] == username:
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


@app.route("/settings", methods=['GET'])
def editusersettings():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('settings.html', friends_ph=db.getfriends(),
                               competitors_ph=db.getcompetitors(), alexa_rank_ph=db.alexarankfilter(),
                               color=db.getcolors())


@app.route("/edit_settings", methods=['POST'])
def edit_settings():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        friendslist = []
        for x in request.form['friends'].split('\r\n'):
            if x != '':
                friendslist.append(x)

        if friendslist != db.getfriends():
            db.user.find_one_and_update({"friends": db.getfriends()},
                                        {"$set": {"friends": friendslist}})
        competitorlist = []
        for x in request.form['competitors'].split('\r\n'):
            if x != '':
                competitorlist.append(x)

        if competitorlist != db.getcompetitors():
            db.user.find_one_and_update({"competitors": db.getcompetitors()},
                                        {"$set": {"competitors": competitorlist}})
        if str(request.form['alexa_rank']) != str(db.alexarankfilter()):
            db.site.find_one_and_update({"alexa_filter_rank": db.alexarankfilter()},
                                        {"$set": {"alexa_filter_rank": request.form['alexa_rank']}})
        if str(request.form['alexa200']) != str(db.getcolors()[0]):
            db.site.find_one_and_update({"alexa200": db.getcolors()[0]},
                                        {"$set": {"alexa200": request.form['alexa200']}})
        if str(request.form['alexa400']) != str(db.getcolors()[1]):
            db.site.find_one_and_update({"alexa400": db.getcolors()[1]},
                                        {"$set": {"alexa400": request.form['alexa400']}})
        if str(request.form['alexa600']) != str(db.getcolors()[2]):
            db.site.find_one_and_update({"alexa600": db.getcolors()[2]},
                                        {"$set": {"alexa600": request.form['alexa600']}})
        if str(request.form['alexa800']) != str(db.getcolors()[3]):
            db.site.find_one_and_update({"alexa800": db.getcolors()[3]},
                                        {"$set": {"alexa800": request.form['alexa800']}})
        if str(request.form['alexa1000']) != str(db.getcolors()[4]):
            db.site.find_one_and_update({"alexa1000": db.getcolors()[4]},
                                        {"$set": {"alexa1000": request.form['alexa1000']}})
        return editusersettings()


@app.route("/best_result", methods=['GET'])
def get_best_result():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        items = db.getallitems()
        lista = list()
        for x in items:
            if x['backlinks_competitor'] == 0:
                if x['malware_status'] == 'Clean':
                    if int(x['alexa_rank']) < db.alexarankfilter() and int(x['alexa_rank']) > 0:
                        lista.append(x)
        return render_template("best_result.html", items=lista, color=db.getcolors())


@app.route("/best_result_history", methods=['GET'])
def get_best_result_history():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        theid = request.args.get('itemid')
        items = db.getonehistoryitem(theid)
        lista = list()
        for x in items['report']:
            if x['backlinks_competitor'] == 0:
                if x['malware_status'] == 'Clean':
                    if int(x['alexa_rank']) < db.alexarankfilter() and int(x['alexa_rank']) > 0:
                        lista.append(x)
        return render_template("best_result.html", items=lista, mainid=theid, color=db.getcolors())


@app.route("/get_keywords", methods=['GET'])
def editkw():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        grup = request.args.get('group')
        keywords = db.getkwfromgroup(grup)
        return render_template('kw_file.html', grup=grup, keywords_array=keywords)


@app.route("/add_kws", methods=['POST'])
def addtodb():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        group_name = request.form['group_name']
        kwlist = []
        for x in request.form['keywords'].split('\r\n'):
            if x != '':
                kwlist.append(x)
        item = dict()
        item['name'] = group_name
        item['keywords'] = kwlist
        db.addkwandgroup(item)
        return kw_page()


@app.route("/delkwgroup", methods=['GET'])
def rmfromdb():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        grup = request.args.get('group')
        db.deletekwgroup(grup)
        return kw_page()


@app.route("/start", methods=['POST'])
def startreporting():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        grup = request.form['grup']
        client = main.MainApp(kw=db.getkwfromgroup(grup), friends=db.getfriends(), competitors=db.getcompetitors())
        client.startapp()
        db.clearitems()
        for x in client.all_items:
            db.additemsalone(x)
        db.updatepurls(len(client.all_items))
        db.updatecrawls()
        istoric = dict()
        istoric['date'] = datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')
        istoric['group_name'] = grup
        istoric['keywords'] = db.getkwfromgroup(grup)
        istoric['method'] = "Auto"
        istoric['report'] = client.all_items
        db.addtohistory(istoric)
        client.resetitems()

        return render_template("report.html", items=db.getallitems(), color=db.getcolors(), grup=grup,
                               kw=db.getkwfromgroup(grup))


@app.route("/history_list", methods=['GET'])
def get_history():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        lista = db.readhistory()
        return render_template("history_list.html", lista=lista)


@app.route('/get_history_report', methods=['GET'])
def get_history_obj():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        idul = request.args.get('id')
        item = db.readhistoryreport(idul)
        return render_template('history_report.html', item=item, color=db.getcolors())


@app.route("/start_report", methods=['GET'])
def beginreport():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template("start_report.html", kwgroups=db.readkwgroup())


@app.route("/get_details", methods=['GET'])
def getiteminfo():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if request.args.get('main_id') != '':
            idul = request.args.get('id')
            main_id = request.args.get('main_id')
            item = db.getonehistoryitem(main_id)
            if not item:
                idul = request.args.get('id')
                item = db.getoneitem(idul)
                return render_template("details.html", item=item, color=db.getcolors())
            else:
                for x in item['report']:
                    if str(x['_id']) == str(idul):
                        return render_template("details.html", item=x, color=db.getcolors())
        else:
            idul = request.args.get('id')
            item = db.getoneitem(idul)
            return render_template("details.html", item=item, color=db.getcolors())


@app.route("/updatekw", methods=['POST'])
def updatekws():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        grup = request.form['grup']
        keywords = request.form['keywords']
        kwlst = []
        for x in keywords.split('\r\n'):
            if x != '':
                kwlst.append(x)
        if kwlst != db.getkwfromgroup(grup):
            db.kwgroup.find_one_and_update({"name": grup},
                                           {"$set": {"keywords": kwlst}})
        return kw_page()


@app.route("/keywords", methods=['GET'])
def kw_page():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('keywords.html', kwgroups=db.readkwgroup())


@app.route("/manual_search", methods=['GET'])
def manual_search():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template("manual.html")


@app.route("/delete_report", methods=['GET'])
def delreport():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        idul = request.args.get('id')
        db.deletereport(idul)
        return get_history()


@app.route("/manual", methods=['POST'])
def manual():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        lista = request.form['list']
        kwlst = []
        for x in lista.split('\r\n'):
            if x != '':
                kwlst.append(x)
        client = main.MainApp(kw=None, friends=db.getfriends(), competitors=db.getcompetitors())
        client.resetitems()
        client.manualsearch(kwlst)
        db.clearitems()
        for x in client.all_items:
            db.additemsalone(x)
        db.updatepurls(len(client.all_items))
        db.updatecrawls()
        istoric = dict()
        istoric['date'] = datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')
        istoric['group_name'] = "-"
        istoric['method'] = "Manual"
        istoric['report'] = client.all_items
        db.addtohistory(istoric)
        client.resetitems()
        return render_template("report.html", items=db.getallitems(), color=db.getcolors())


if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=52166)
