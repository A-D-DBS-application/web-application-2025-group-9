CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) NOT NULL UNIQUE,
    user_name VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE companies (
    company_id VARCHAR(36) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    company_address VARCHAR(500),
    vat_number VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    credit_score NUMERIC(10, 2),
    solvency_ratio NUMERIC(10, 2),
    debt_ratio NUMERIC(10, 2),
    established_since DATE,
    revenue_estimation VARCHAR(50),
    employee_estimation VARCHAR(50),
    common_score VARCHAR(10),
    credit_limit NUMERIC(15, 2),
    current_ratio NUMERIC(10, 4),
    quick_ratio NUMERIC(10, 4),
    cash NUMERIC(15, 2),
    ebitda NUMERIC(15, 2),
    net_profit NUMERIC(15, 2),
    total_assets NUMERIC(15, 2),
    equity NUMERIC(15, 2),
    total_debt NUMERIC(15, 2),
    deleted_at TIMESTAMP
);


CREATE TABLE debtor_batches (
    batch_id SERIAL PRIMARY KEY,
    batch_name VARCHAR(255) NOT NULL,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    deleted_at TIMESTAMP
);

-- Cases Table
CREATE TABLE cases (
    case_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id VARCHAR(36) NOT NULL REFERENCES companies(company_id),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    batch_id INTEGER REFERENCES debtor_batches(batch_id) ON DELETE SET NULL,
    amount NUMERIC(15, 2) NOT NULL DEFAULT 0,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    is_debtor BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);


CREATE INDEX idx_cases_company_id ON cases(company_id);
CREATE INDEX idx_cases_user_id ON cases(user_id);
CREATE INDEX idx_cases_batch_id ON cases(batch_id);
CREATE INDEX idx_debtor_batches_user_id ON debtor_batches(user_id);
CREATE INDEX idx_companies_vat_number ON companies(vat_number);
