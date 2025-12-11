from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


# =====================================================
# AUTHENTICATION & USER MANAGEMENT
# =====================================================

class Role(db.Model):
    """User roles (bailiff, legal associate, firm admin, compliance officer, etc.)"""
    __tablename__ = 'roles'
    
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relationships
    users = db.relationship('User', backref='role', lazy=True)
    
    def __repr__(self):
        return f"<Role {self.role_name}>"


class LoginGegevens(db.Model):
    """Login credentials (authentication table)"""
    __tablename__ = 'inlog_gegevens'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naam = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key to users table
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user = db.relationship('User', backref='login_credentials', uselist=False)
    
    def __repr__(self):
        return f"<LoginGegevens {self.naam}>"


class User(db.Model):
    """User profile information"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key to roles
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    
    # Relationships
    cases = db.relationship('Case', backref='user', lazy=True, foreign_keys='Case.user_id')
    
    def __repr__(self):
        return f"<User {self.user_name}>"


# =====================================================
# COMPANY & FINANCIAL DATA
# =====================================================

class Company(db.Model):
    """Company information with financial health metrics"""
    __tablename__ = 'companies'
    
    company_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = db.Column(db.String(255), nullable=False)
    company_address = db.Column(db.String(500))
    vat_number = db.Column(db.String(50), unique=True)  # BTW-nummer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    credit_score = db.Column(db.Numeric(10, 2))
    solvency_ratio = db.Column(db.Numeric(10, 2))
    debt_ratio = db.Column(db.Numeric(10, 2))
    sector = db.Column(db.String(255))
    
    # Relationships
    cases = db.relationship('Case', backref='company', lazy=True, foreign_keys='Case.company_id')
    
    def __repr__(self):
        return f"<Company {self.company_name}>"
    
    def calculate_solvency_score(self):
        """Calculate solvency score based on financial metrics"""
        if not all([self.solvency_ratio, self.debt_ratio, self.credit_score]):
            return None
        
        score = (
            float(self.solvency_ratio) * 0.5 +
            (100 - float(self.debt_ratio)) * 0.3 +
            (float(self.credit_score) / 10) * 0.2
        )
        return round(score, 2)


class Company1(db.Model):
    """Alternative company data table (structure to be determined)"""
    __tablename__ = 'companies1'
    
    company_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255))
    
    # Relationships
    statements = db.relationship('Statement', backref='company_alt', lazy=True)
    
    def __repr__(self):
        return f"<Company1 {self.name}>"


# =====================================================
# CASE MANAGEMENT
# =====================================================

class Case(db.Model):
    """Bailiff cases linked to companies and users"""
    __tablename__ = 'cases'
    
    case_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.company_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2))
    status = db.Column(db.String(50))  # case-status type in DB
    is_debtor = db.Column(db.Boolean, default=False)  # Flag for debtor list
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Case {self.case_id} - {self.status}>"


# =====================================================
# FINANCIAL STATEMENTS & REFERENCE DATA
# =====================================================

class Table(db.Model):
    """Reference table for statements"""
    __tablename__ = 'tables'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    statement_id = db.Column(db.String(100))  # Link to statements
    table_name = db.Column(db.String(255))
    
    def __repr__(self):
        return f"<Table {self.table_name}>"


class Statement(db.Model):
    """Financial statements for companies"""
    __tablename__ = 'statements'
    
    id = db.Column(db.Integer, db.ForeignKey('tables.id'), primary_key=True)
    company_id = db.Column(db.String(36), db.ForeignKey('companies1.company_id'), nullable=False)
    year = db.Column(db.Integer)
    activa = db.Column(db.Numeric(15, 2))
    oprichtingskosten = db.Column(db.Numeric(15, 2))
    vaste_activa = db.Column(db.Numeric(15, 2))
    immateriële_activa = db.Column(db.Numeric(15, 2))
    source_date = db.Column(db.Date)
    file_name = db.Column(db.String(500))  # PDF file name or URL
    inserted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Statement {self.company_id} - {self.year}>"
