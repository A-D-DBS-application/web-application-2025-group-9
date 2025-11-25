from flask import Flask, request, render_template, redirect, url_for, session
from supabase import create_client, Client
import bcrypt

app = Flask(__name__)
print(app.url_map)

app.secret_key = "een_veilige_random_sleutel"


SUPABASE_URL = "https://rhhnxaxbtapjenunokzv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoaG54YXhidGFwamVudW5va3p2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjI0MTM1OSwiZXhwIjoyMDc3ODE3MzU5fQ.pOzo8T7A98uckDyeVIjJc0ZI1tHhPpY_KR8OWNkgmBM"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# HOME (LOGIN PAGINA)
# -------------------------
@app.route('/')
def home():
    return render_template('login.html')


# -------------------------
# REGISTRATIE PAGINA
# -------------------------
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')


# -------------------------
# LOGIN VERWERKING
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    # POST → inloggen
    naam = request.form.get("naam")
    password = request.form.get("password")

    result = supabase.table("inlog_gegevens").select("*").eq("naam", naam).execute()

    if not result.data:
        return render_template("login.html", error="Gebruiker bestaat niet")

    user = result.data[0]
    stored_pw = user["password"]

    if bcrypt.checkpw(password.encode('utf-8'), stored_pw.encode('utf-8')):
        session['user'] = naam
        return redirect(url_for('dashboard'))
    else:
        return render_template("login.html", error="Wachtwoord is incorrect")

    


@app.route('/account_created')
def account_created():
    return render_template('account_created.html')


# -------------------------
# REGISTRATIE VERWERKING
# -------------------------
@app.route('/register', methods=['POST'])
def register():
    rol = request.form.get("rol")
    naam = request.form.get("naam")
    password = request.form.get("password")
    password2 = request.form.get("password2")

    # 1. Controle: wachtwoorden gelijk?
    if password != password2:
        return render_template("register.html", error="Wachtwoorden zijn niet gelijk!")

    # 2. Controle: bestaat gebruiker al?
    check = supabase.table("inlog_gegevens").select("*").eq("naam", naam).execute()

    if check.data:
        return render_template("register.html", error="Gebruiker bestaat al!")

    # 3. Hash wachtwoord
    hashed_pw = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    # 4. Opslaan in Supabase
    supabase.table("inlog_gegevens").insert({
        "naam": naam,
        "password": hashed_pw
        "rol": rol
    }).execute()

    session['user'] = naam    # automatisch inloggen
    return redirect(url_for('account_created'))


@app.route('/dashboard', methods=['GET'])
def dashboard():
    user = session.get("user")
    query = request.args.get("q")  # zit iets in de zoekbalk?

    # Geen zoekopdracht → toon lege pagina
    if not query:
        return render_template("dashboard.html", user=user)

    # Zoek in Supabase
    result = supabase.table("companies") \
                     .select("*") \
                     .ilike("company_name", f"%{query}%") \
                     .execute()

    companies = result.data

    # Geen enkel bedrijf gevonden
    if not companies:
        return render_template("dashboard.html", user=user,
                               error="Geen bedrijf gevonden in de BEL20.")

    # Wel bedrijven gevonden → toon ze onder het zoekvak
    return render_template("dashboard.html", user=user, companies=companies)


@app.route('/logout')
def logout():
    session.pop('user', None)   # verwijdert ingelogde gebruiker
    return redirect(url_for('dashboard'))


@app.route('/company/<company_id>')
def company(company_id):
    result = supabase.table("companies") \
                     .select("*") \
                     .eq("company_id", company_id) \
                     .execute()

    if not result.data:
        return "Bedrijf niet gevonden", 404

    company = result.data[0]

    return render_template("company.html", company=company)


@app.route('/score/<company_id>')
def score(company_id):
    result = supabase.table("companies") \
                     .select("*") \
                     .eq("company_id", company_id) \
                     .execute()

    company = result.data[0]

    score = (
        company["solvency_ratio"] * 0.5 +
        (100 - company["debt_ratio"]) * 0.3 +
        (company["credit_score"] / 10) * 0.2
    )

    score = round(score, 2)

    return render_template("score.html", company=company, score=score)




if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
