from flask import Blueprint, request, redirect, url_for, render_template, session
from .models import db, LoginGegevens, User, Company, Case, Role
from .api_client import get_company_financials

main = Blueprint("main", __name__)


# =====================================================
# AUTHENTICATION ROUTES
# =====================================================

@main.route("/")
def index():
    """Home page - redirect to login or dashboard based on session"""
    if session.get("user"):
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    """Login route - authenticate user with username only"""
    if request.method == "GET":
        return render_template("login.html")
    
    # POST - Process login
    naam = request.form.get("naam")
    
    # Find user by login username
    login_user = LoginGegevens.query.filter_by(naam=naam).first()
    
    if not login_user:
        return render_template("login.html", error="Gebruiker bestaat niet")
    
    # No password check needed - open access
    session['user'] = naam
    session['user_id'] = login_user.user_id
    return redirect(url_for("main.dashboard"))


@main.route("/register", methods=["GET", "POST"])
def register():
    """Registration route - create new user account"""
    if request.method == "GET":
        # Fetch roles for dropdown selection
        roles = Role.query.all()
        return render_template("register.html", roles=roles)
    
    # POST - Process registration
    rol_id = request.form.get("rol")
    naam = request.form.get("naam")
    user_name = request.form.get("user_name", naam)  # Default to naam if not provided
    user_email = request.form.get("user_email")
    
    # Validation: Username doesn't exist
    existing_login = LoginGegevens.query.filter_by(naam=naam).first()
    if existing_login:
        roles = Role.query.all()
        return render_template("register.html", error="Gebruiker bestaat al!", roles=roles)
    
    # Validation: Email doesn't exist
    existing_email = User.query.filter_by(user_email=user_email).first()
    if existing_email:
        roles = Role.query.all()
        return render_template("register.html", error="Email bestaat al!", roles=roles)
    
    # Create new User
    new_user = User(
        user_name=user_name,
        user_email=user_email,
        role_id=rol_id
    )
    db.session.add(new_user)
    db.session.flush()  # Flush to get user_id without committing
    
    # Create new LoginGegevens linked to User (no password)
    new_login = LoginGegevens(
        naam=naam,
        user_id=new_user.user_id
    )
    db.session.add(new_login)
    db.session.commit()
    
    # Auto-login
    session['user'] = naam
    session['user_id'] = new_user.user_id
    
    return redirect(url_for("main.account_created"))


@main.route("/account_created")
def account_created():
    """Account created confirmation page"""
    return render_template("account_created.html")


@main.route("/logout")
def logout():
    """Logout route - clear session"""
    session.pop('user', None)
    session.pop('user_id', None)
    return redirect(url_for("main.login"))


# =====================================================
# DASHBOARD & SEARCH ROUTES
# =====================================================

@main.route("/dashboard", methods=["GET"])
def dashboard():
    """Dashboard route - search and display companies"""
    user = session.get("user")
    query = request.args.get("q")
    companies = None
    error = None
    
    # If no search query, show empty dashboard
    if not query:
        return render_template("dashboard.html", user=user, companies=companies)
    
    # Check if query looks like a VAT number
    import re
    vat_pattern = re.compile(r'^BE\s?\d{4}\.?\d{3}\.?\d{3}$')
    if vat_pattern.match(query.strip()):
        # Clean the VAT number (remove spaces and dots)
        clean_vat = query.replace(' ', '').replace('.', '')
        return redirect(url_for('main.search_vat', vat_number=clean_vat))
    
    # Search companies by name
    companies = Company.query.filter(
        Company.company_name.ilike(f"%{query}%")
    ).all()
    
    # No results found
    if not companies:
        error = "Geen bedrijf gevonden"
        return render_template("dashboard.html", user=user, error=error)
    
    return render_template("dashboard.html", user=user, companies=companies)


@main.route("/search_vat/<vat_number>")
def search_vat(vat_number):
    """Search company by VAT number and fetch data from bizzy.ai API"""
    try:
        # Fetch data from API
        api_data = get_company_financials(vat_number)
        
        # Find or create company record
        company = Company.query.filter_by(vat_number=vat_number).first()
        if not company:
            company = Company(vat_number=vat_number)
        
        # Update with API data
        company.company_name = api_data.get('company_name')
        company.credit_score = api_data.get('credit_score')
        company.solvency_ratio = api_data.get('solvency_ratio')
        company.debt_ratio = api_data.get('debt_ratio')
        company.sector = api_data.get('sector')
        
        db.session.add(company)
        db.session.commit()
        
        # Redirect to company detail page
        return redirect(url_for("main.company", company_id=company.company_id))
        
    except Exception as e:
        # On error, redirect back to dashboard with error
        return redirect(url_for("main.dashboard"))


# =====================================================
# COMPANY DETAIL ROUTES
# =====================================================

@main.route("/company/<company_id>")
def company(company_id):
    """Company details page"""
    company = Company.query.filter_by(company_id=company_id).first()
    
    if not company:
        return "Bedrijf niet gevonden", 404
    
    return render_template("company.html", company=company)


@main.route("/score/<company_id>")
def score(company_id):
    """Solvency score page - calculate and display company score"""
    company = Company.query.filter_by(company_id=company_id).first()
    
    if not company:
        return "Bedrijf niet gevonden", 404
    
    # Calculate solvency score using model method
    score = company.calculate_solvency_score()
    
    return render_template("score.html", company=company, score=score)


@main.route("/debtors")
def debtors():
    """Display list of debtor companies sorted by credit score"""
    user = session.get("user")
    if not user:
        return redirect(url_for("main.login"))
    
    # Get user's cases that are marked as debtors
    debtor_cases = Case.query.filter_by(user_id=session['user_id'], is_debtor=True).all()
    
    # Sort by solvency score (ascending - lowest score first)
    sorted_cases = sorted(debtor_cases, key=lambda c: c.company.calculate_solvency_score() or 0)
    
    return render_template("debtors.html", user=user, cases=sorted_cases)


@main.route("/add_debtor/<company_id>", methods=["POST"])
def add_debtor(company_id):
    """Add a company to the debtor list"""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("main.login"))

    # Find a case for this user and company
    case = Case.query.filter_by(company_id=company_id, user_id=user_id).first()

    if not case:
        # Create a new case linking the user and company
        case = Case(company_id=company_id, user_id=user_id)

    case.is_debtor = True
    db.session.add(case)
    db.session.commit()

    return redirect(url_for("main.company", company_id=company_id))