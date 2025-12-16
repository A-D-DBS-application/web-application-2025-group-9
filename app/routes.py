from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from .models import db, LoginGegevens, User, Company, Case, Role, DebtorBatch
from .api_client import get_company_financials
import re
import csv
import io
from datetime import datetime

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
    
    # Check if query could be a VAT number (BTW-nummer)
    import re
    # Normalize the query: uppercase, remove spaces, dots, and hyphens
    normalized_query = query.upper().replace(' ', '').replace('.', '').replace('-', '')

    # Check if it looks like a Belgian VAT number with BE prefix
    if normalized_query.startswith('BE') and normalized_query[2:].isdigit() and len(normalized_query) in [11, 12]:
        # The VAT number is already clean and normalized
        return redirect(url_for('main.search_vat', vat_number=normalized_query))
    
    # Check if it's a 9 or 10 digit number (Belgian VAT without BE prefix)
    if normalized_query.isdigit() and len(normalized_query) in [9, 10]:
        # Prepend BE to make it a full Belgian VAT number
        return redirect(url_for('main.search_vat', vat_number=f'BE{normalized_query}'))
    
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
        # Clean VAT number for storage consistency
        clean_vat = f"BE{vat_number.replace('BE', '').replace(' ', '').replace('.', '').replace('-', '')}"
        
        # Fetch comprehensive data from API (Details + Financials)
        api_data = get_company_financials(clean_vat)
        
        # Find or create company record using clean VAT number
        company = Company.query.filter_by(vat_number=clean_vat).first()
        if not company:
            company = Company(vat_number=clean_vat)
        
        # Update with all API data
        company.company_name = api_data.get('company_name')
        company.company_address = api_data.get('company_address')
        company.legal_status = api_data.get('legal_status')
        company.established_since = api_data.get('established_since')
        company.revenue_estimation = api_data.get('revenue_estimation')
        company.employee_estimation = api_data.get('employee_estimation')
        company.common_score = api_data.get('common_score')
        company.credit_limit = api_data.get('credit_limit')
        company.credit_score = api_data.get('credit_score')
        company.solvency_ratio = api_data.get('solvency_ratio')
        company.debt_ratio = api_data.get('debt_ratio')
        company.current_ratio = api_data.get('current_ratio')
        company.quick_ratio = api_data.get('quick_ratio')
        company.ebitda = api_data.get('ebitda')
        company.net_profit = api_data.get('net_profit')
        company.total_assets = api_data.get('total_assets')
        company.equity = api_data.get('equity')
        company.total_debt = api_data.get('total_debt')
        company.sector = api_data.get('sector')
        
        db.session.add(company)
        db.session.commit()
        
        # Redirect to company detail page
        return redirect(url_for("main.company", company_id=company.company_id))
        
    except Exception as e:
        # On error, redirect back to dashboard with error
        import traceback
        print(f"Error in search_vat: {str(e)}")
        print(traceback.format_exc())
        flash(f"Fout bij opzoeken bedrijf: {str(e)}", "danger")
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


@main.route("/debtors")
def debtors():
    """Display batches and search debtors"""
    user = session.get("user")
    if not user:
        return redirect(url_for("main.login"))
    
    search_query = request.args.get("search", "").strip()
    
    # Get all batches for this user
    batches = DebtorBatch.query.filter_by(user_id=session['user_id']).order_by(DebtorBatch.created_at.desc()).all()
    
    # Get standalone debtors (not in any batch)
    standalone_debtors = Case.query.filter_by(
        user_id=session['user_id'], 
        is_debtor=True,
        batch_id=None
    ).all()
    
    # Search functionality
    search_results = []
    if search_query:
        # Search in all batches for companies matching the query
        all_cases = Case.query.filter_by(user_id=session['user_id']).join(Company).filter(
            (Case.batch_id.isnot(None)) | (Case.is_debtor == True)
        ).all()
        
        for case in all_cases:
            if search_query.lower() in case.company.company_name.lower():
                search_results.append({
                    'case': case,
                    'batch': case.batch if case.batch_id else None
                })
    
    return render_template("debtors.html", 
                         user=user, 
                         batches=batches,
                         standalone_debtors=standalone_debtors,
                         search_query=search_query,
                         search_results=search_results)


@main.route("/add_debtor/<company_id>", methods=["GET", "POST"])
def add_debtor(company_id):
    """Add a company to the debtor list (with optional batch selection)"""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("main.login"))

    if request.method == "GET":
        # Show form to select batch or create new one
        batches = DebtorBatch.query.filter_by(user_id=user_id).order_by(DebtorBatch.created_at.desc()).all()
        company = Company.query.get(company_id)
        return render_template("add_to_batch.html", company=company, batches=batches)
    
    # POST: Determine which option was selected
    option = request.form.get("option")
    batch_id = None
    
    if option == "existing":
        batch_id = request.form.get("batch_id")
    elif option == "new":
        new_batch_name = request.form.get("new_batch_name", "").strip()
        if new_batch_name:
            new_batch = DebtorBatch(
                batch_name=new_batch_name,
                user_id=user_id,
                description=request.form.get("batch_description", "")
            )
            db.session.add(new_batch)
            db.session.flush()
            batch_id = new_batch.batch_id
    # option == "standalone" means batch_id stays None
    
    # Check if company already exists in the batch (prevent duplicates)
    if batch_id:
        existing_case = Case.query.filter_by(
            company_id=company_id,
            batch_id=batch_id
        ).first()
        
        if existing_case:
            flash("Dit bedrijf zit al in deze batch", "warning")
            return redirect(url_for('main.add_debtor', company_id=company_id))
    
    # Create case
    case = Case(
        company_id=company_id, 
        user_id=user_id,
        batch_id=batch_id if batch_id else None,
        amount=0,
        status='pending',
        is_debtor=True if not batch_id else False  # Standalone if no batch
    )
    
    db.session.add(case)
    db.session.commit()
    
    flash(f"Bedrijf succesvol toegevoegd!", "success")
    return redirect(url_for("main.debtors"))


@main.route("/upload_csv", methods=["GET", "POST"])
def upload_csv():
    """Upload CSV file with VAT numbers to create a batch"""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("main.login"))
    
    if request.method == "GET":
        return render_template("upload_csv.html")
    
    # Handle file upload
    if 'csv_file' not in request.files:
        flash("Geen bestand geselecteerd", "danger")
        return redirect(url_for("main.upload_csv"))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash("Geen bestand geselecteerd", "danger")
        return redirect(url_for("main.upload_csv"))
    
    batch_name = request.form.get("batch_name", f"Batch {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    batch_description = request.form.get("batch_description", "")
    
    # Create batch
    batch = DebtorBatch(
        batch_name=batch_name,
        user_id=user_id,
        description=batch_description
    )
    db.session.add(batch)
    db.session.flush()
    
    # Read CSV file
    try:
        file_content = file.stream.read().decode("UTF-8")
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        file.stream.seek(0)
        file_content = file.stream.read().decode("latin-1")
    
    # Parse VAT numbers (handle both comma-separated, semicolon-separated, and line-separated)
    vat_numbers = []
    
    # Split by newlines first
    lines = file_content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line contains commas or semicolons (CSV format)
        if ',' in line or ';' in line:
            # Split by both comma and semicolon
            separators = [',', ';']
            parts = [line]
            for sep in separators:
                new_parts = []
                for part in parts:
                    new_parts.extend(part.split(sep))
                parts = new_parts
            
            # Process each value
            for vat in parts:
                vat = vat.strip()
                # Remove quotes if present (from Excel CSV)
                vat = vat.strip('"').strip("'").strip()
                if vat and not vat.lower().startswith('vat'):  # Skip header if present
                    vat_numbers.append(vat)
        else:
            # Single VAT per line
            vat = line.strip('"').strip("'").strip()
            if vat and not vat.lower().startswith('vat'):
                vat_numbers.append(vat)
    
    # Remove duplicates while preserving order
    vat_numbers = list(dict.fromkeys(vat_numbers))
    
    # Process each VAT number
    success_count = 0
    error_list = []
    
    for vat in vat_numbers:
        try:
            # Clean VAT number
            clean_vat = f"BE{vat.replace('BE', '').replace(' ', '').replace('.', '').replace('-', '')}"
            
            # Fetch data from API
            api_data = get_company_financials(clean_vat)
            
            # Find or create company
            company = Company.query.filter_by(vat_number=clean_vat).first()
            if not company:
                company = Company(vat_number=clean_vat)
            
            # Update with API data
            company.company_name = api_data.get('company_name')
            company.company_address = api_data.get('company_address')
            company.legal_status = api_data.get('legal_status')
            company.established_since = api_data.get('established_since')
            company.revenue_estimation = api_data.get('revenue_estimation')
            company.employee_estimation = api_data.get('employee_estimation')
            company.common_score = api_data.get('common_score')
            company.credit_limit = api_data.get('credit_limit')
            company.credit_score = api_data.get('credit_score')
            company.solvency_ratio = api_data.get('solvency_ratio')
            company.debt_ratio = api_data.get('debt_ratio')
            company.current_ratio = api_data.get('current_ratio')
            company.quick_ratio = api_data.get('quick_ratio')
            company.cash = api_data.get('cash')
            company.ebitda = api_data.get('ebitda')
            company.net_profit = api_data.get('net_profit')
            company.total_assets = api_data.get('total_assets')
            company.equity = api_data.get('equity')
            company.total_debt = api_data.get('total_debt')
            
            db.session.add(company)
            db.session.flush()
            
            # Check if this company is already in the batch (skip duplicates)
            existing_case = Case.query.filter_by(
                company_id=company.company_id,
                batch_id=batch.batch_id
            ).first()
            
            if existing_case:
                # Skip this company, already in batch
                continue
            
            # Create case for this company in the batch
            case = Case(
                company_id=company.company_id,
                user_id=user_id,
                batch_id=batch.batch_id,
                amount=0,
                status='pending',
                is_debtor=False  # Part of batch, not standalone
            )
            db.session.add(case)
            success_count += 1
            
        except Exception as e:
            error_list.append(f"{vat}: {str(e)}")
    
    db.session.commit()
    
    # Provide feedback
    if success_count == 0:
        flash(f"Waarschuwing: Geen bedrijven toegevoegd. Gevonden BTW-nummers: {', '.join(vat_numbers[:5]) if vat_numbers else 'Geen'}", "warning")
        if error_list:
            for error in error_list[:5]:  # Show first 5 errors
                flash(f"Fout: {error}", "danger")
    else:
        flash(f"Batch '{batch_name}' aangemaakt met {success_count} bedrijven", "success")
        if error_list:
            flash(f"Fouten bij {len(error_list)} bedrijven: {', '.join(error_list[:3])}", "warning")
    
    return redirect(url_for("main.batch_detail", batch_id=batch.batch_id))


@main.route("/batch/<int:batch_id>")
def batch_detail(batch_id):
    """View details of a specific batch"""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("main.login"))
    
    batch = DebtorBatch.query.get_or_404(batch_id)
    
    # Security check
    if str(batch.user_id) != str(user_id):
        flash("Geen toegang tot deze batch", "danger")
        return redirect(url_for("main.debtors"))
    
    # Get cases in this batch
    cases = Case.query.filter_by(batch_id=batch_id).all()
    
    # Sort by quick ratio (higher = better liquidity = visit first)
    # Then by cash on hand (higher = more money available)
    sorted_cases = sorted(cases, key=lambda c: (
        -(float(c.company.quick_ratio) if c.company.quick_ratio else -999),  # Higher quick ratio first
        -(float(c.company.cash) if c.company.cash else -999)  # Higher cash first
    ))
    
    return render_template("batch_detail.html", batch=batch, cases=sorted_cases)


@main.route("/batch/<int:batch_id>/export_pdf")
def export_batch_pdf(batch_id):
    """Export batch to PDF"""
    from xhtml2pdf import pisa
    from flask import make_response
    from datetime import datetime
    from io import BytesIO
    
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("main.login"))
    
    # Get batch using ORM
    batch = DebtorBatch.query.get_or_404(batch_id)
    
    # Security check
    if str(batch.user_id) != str(user_id):
        flash("Geen toegang tot deze batch", "danger")
        return redirect(url_for("main.debtors"))
    
    # Get cases using ORM
    cases = Case.query.filter_by(batch_id=batch_id).all()
    
    # Sort by quick ratio (primary) then cash (secondary)
    sorted_cases = sorted(cases, key=lambda c: (
        -(float(c.company.quick_ratio) if c.company.quick_ratio else -999),
        -(float(c.company.cash) if c.company.cash else -999)
    ))
    
    # Render HTML template
    html_string = render_template("batch_pdf.html", 
                                 batch=batch, 
                                 cases=sorted_cases,
                                 export_date=datetime.now())
    
    # Convert to PDF
    pdf_file = BytesIO()
    pisa.CreatePDF(html_string, dest=pdf_file)
    pdf_file.seek(0)
    
    # Return as download
    response = make_response(pdf_file.read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=batch_{batch.batch_name.replace(' ', '_')}.pdf"
    
    return response


@main.route("/batch/<int:batch_id>/delete", methods=["POST"])
def delete_batch(batch_id):
    """Delete an entire batch and all its cases"""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("main.login"))
    
    batch = DebtorBatch.query.get_or_404(batch_id)
    
    # Security check
    if str(batch.user_id) != str(user_id):
        flash("Geen toegang tot deze batch", "danger")
        return redirect(url_for("main.debtors"))
    
    batch_name = batch.batch_name
    
    # Delete all cases in this batch
    Case.query.filter_by(batch_id=batch_id).delete()
    
    # Delete the batch
    db.session.delete(batch)
    db.session.commit()
    
    flash(f"Batch '{batch_name}' verwijderd", "success")
    return redirect(url_for("main.debtors"))


@main.route("/debtor/<case_id>/delete", methods=["POST"])
def delete_debtor(case_id):
    """Delete a single debtor (case)"""
    import uuid as uuid_lib
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("main.login"))
    
    # Convert case_id string to UUID
    try:
        case_uuid = uuid_lib.UUID(case_id)
    except ValueError:
        flash("Ongeldige case ID", "danger")
        return redirect(url_for("main.debtors"))
    
    case = Case.query.get_or_404(case_uuid)
    
    # Security check
    if str(case.user_id) != str(user_id):
        flash("Geen toegang", "danger")
        return redirect(url_for("main.debtors"))
    
    batch_id = case.batch_id
    company_name = case.company.company_name
    
    db.session.delete(case)
    db.session.commit()
    
    flash(f"'{company_name}' verwijderd", "success")
    
    # Redirect back to batch if it was part of one
    if batch_id:
        return redirect(url_for("main.batch_detail", batch_id=batch_id))
    else:
        return redirect(url_for("main.debtors"))