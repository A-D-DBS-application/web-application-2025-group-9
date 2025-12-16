from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
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


class User(db.Model):
    """User profile information and authentication"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)  # For login
    user_name = db.Column(db.String(255), nullable=False)  # Display name
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
    
    # Basic financial metrics
    credit_score = db.Column(db.Numeric(10, 2))
    solvency_ratio = db.Column(db.Numeric(10, 2))
    debt_ratio = db.Column(db.Numeric(10, 2))
    
    # New fields from Details API
    established_since = db.Column(db.Date)
    revenue_estimation = db.Column(db.String(50))
    employee_estimation = db.Column(db.String(50))
    common_score = db.Column(db.String(10))  # A, B, C, D, E
    credit_limit = db.Column(db.Numeric(15, 2))
    
    # New fields from Financials API
    current_ratio = db.Column(db.Numeric(10, 4))
    quick_ratio = db.Column(db.Numeric(10, 4))
    cash = db.Column(db.Numeric(15, 2))  # Cash and cash equivalents
    ebitda = db.Column(db.Numeric(15, 2))
    net_profit = db.Column(db.Numeric(15, 2))
    total_assets = db.Column(db.Numeric(15, 2))
    equity = db.Column(db.Numeric(15, 2))
    total_debt = db.Column(db.Numeric(15, 2))
    
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


# =====================================================
# CASE MANAGEMENT
# =====================================================

class DebtorBatch(db.Model):
    """Batch of debtors grouped together (e.g., for a collection day)"""
    __tablename__ = 'debtor_batches'
    
    batch_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    batch_name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    
    # Relationships
    cases = db.relationship('Case', backref='batch', lazy=True, foreign_keys='Case.batch_id')
    user = db.relationship('User', backref='debtor_batches', lazy=True)
    
    def __repr__(self):
        return f"<DebtorBatch {self.batch_name}>"


class Case(db.Model):
    """Bailiff cases linked to companies and users"""
    __tablename__ = 'cases'
    
    case_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.company_id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('debtor_batches.batch_id'), nullable=True)  # Link to batch
    amount = db.Column(db.Numeric(15, 2), nullable=False, default=0)
    status = db.Column(db.String(50), nullable=False, default='pending')  # case-status type in DB
    is_debtor = db.Column(db.Boolean, default=False)  # Flag for standalone debtors (no batch)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Case {self.case_id} - {self.status}>"
