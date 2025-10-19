-- Archimedes POC1: Database Schema
-- PostgreSQL 15+

-- Drop existing tables (for development)
DROP TABLE IF EXISTS observations CASCADE;
DROP TABLE IF EXISTS data_freshness CASCADE;
DROP TABLE IF EXISTS countries CASCADE;
DROP TABLE IF EXISTS indicators CASCADE;
DROP TABLE IF EXISTS sources CASCADE;

-- Countries dimension table
CREATE TABLE countries (
    country_code VARCHAR(3) PRIMARY KEY,  -- ISO 3166-1 alpha-3
    country_name VARCHAR(100) NOT NULL,
    region VARCHAR(50),
    income_level VARCHAR(50),  -- High income, Upper middle income, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indicators dimension table
CREATE TABLE indicators (
    indicator_id SERIAL PRIMARY KEY,
    indicator_code VARCHAR(50) UNIQUE NOT NULL,
    indicator_name VARCHAR(200) NOT NULL,
    description TEXT,
    unit VARCHAR(50),  -- %, USD, Index, etc.
    category VARCHAR(50),  -- macroeconomic, financial, social, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data sources dimension table
CREATE TABLE sources (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) UNIQUE NOT NULL,
    source_url VARCHAR(500),
    api_endpoint VARCHAR(500),
    update_frequency VARCHAR(50),  -- daily, monthly, quarterly, annual
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Observations fact table (time series data)
CREATE TABLE observations (
    observation_id BIGSERIAL PRIMARY KEY,
    country_code VARCHAR(3) REFERENCES countries(country_code),
    indicator_id INTEGER REFERENCES indicators(indicator_id),
    source_id INTEGER REFERENCES sources(source_id),
    time_period DATE NOT NULL,  -- Date of observation
    value NUMERIC(20, 4),  -- The actual value
    frequency VARCHAR(10),  -- A (annual), Q (quarterly), M (monthly), D (daily)
    status VARCHAR(20),  -- preliminary, final, revised
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (country_code, indicator_id, source_id, time_period)
);

-- Indexes for query performance
CREATE INDEX idx_observations_country ON observations(country_code);
CREATE INDEX idx_observations_indicator ON observations(indicator_id);
CREATE INDEX idx_observations_time ON observations(time_period);
CREATE INDEX idx_observations_composite ON observations(country_code, indicator_id, time_period);
CREATE INDEX idx_observations_source ON observations(source_id);

-- Metadata table for tracking data freshness
CREATE TABLE data_freshness (
    source_id INTEGER REFERENCES sources(source_id),
    indicator_id INTEGER REFERENCES indicators(indicator_id),
    last_update TIMESTAMP NOT NULL,
    next_update TIMESTAMP,
    record_count INTEGER,
    PRIMARY KEY (source_id, indicator_id)
);

-- Insert sample countries (G20)
INSERT INTO countries (country_code, country_name, region, income_level) VALUES
('USA', 'United States', 'North America', 'High income'),
('CHN', 'China', 'East Asia & Pacific', 'Upper middle income'),
('JPN', 'Japan', 'East Asia & Pacific', 'High income'),
('DEU', 'Germany', 'Europe & Central Asia', 'High income'),
('GBR', 'United Kingdom', 'Europe & Central Asia', 'High income'),
('FRA', 'France', 'Europe & Central Asia', 'High income'),
('IND', 'India', 'South Asia', 'Lower middle income'),
('BRA', 'Brazil', 'Latin America & Caribbean', 'Upper middle income'),
('CAN', 'Canada', 'North America', 'High income'),
('AUS', 'Australia', 'East Asia & Pacific', 'High income'),
('KOR', 'Korea, Rep.', 'East Asia & Pacific', 'High income'),
('MEX', 'Mexico', 'Latin America & Caribbean', 'Upper middle income'),
('IDN', 'Indonesia', 'East Asia & Pacific', 'Lower middle income'),
('SAU', 'Saudi Arabia', 'Middle East & North Africa', 'High income'),
('TUR', 'Turkey', 'Europe & Central Asia', 'Upper middle income'),
('ZAF', 'South Africa', 'Sub-Saharan Africa', 'Upper middle income'),
('ARG', 'Argentina', 'Latin America & Caribbean', 'Upper middle income'),
('ITA', 'Italy', 'Europe & Central Asia', 'High income'),
('RUS', 'Russian Federation', 'Europe & Central Asia', 'Upper middle income');

-- Insert sample indicators
INSERT INTO indicators (indicator_code, indicator_name, description, unit, category) VALUES
('NY.GDP.MKTP.KD.ZG', 'GDP growth (annual %)', 'Annual percentage growth rate of GDP at market prices based on constant local currency', '%', 'macroeconomic'),
('FP.CPI.TOTL.ZG', 'Inflation, consumer prices (annual %)', 'Inflation as measured by the consumer price index reflects the annual percentage change in the cost to the average consumer', '%', 'macroeconomic'),
('SL.UEM.TOTL.ZS', 'Unemployment, total (% of labor force)', 'Unemployment refers to the share of the labor force that is without work but available for and seeking employment', '%', 'macroeconomic'),
('BN.CAB.XOKA.GD.ZS', 'Current account balance (% of GDP)', 'Current account balance as a percentage of GDP', '%', 'macroeconomic'),
('GC.DOD.TOTL.GD.ZS', 'Central government debt, total (% of GDP)', 'Debt is the entire stock of direct government fixed-term contractual obligations to others', '%', 'macroeconomic'),
('GDP', 'Gross Domestic Product', 'US Gross Domestic Product (FRED)', 'Billions of Dollars', 'macroeconomic'),
('CPIAUCSL', 'Consumer Price Index', 'US Consumer Price Index for All Urban Consumers (FRED)', 'Index 1982-84=100', 'macroeconomic'),
('UNRATE', 'Unemployment Rate', 'US Unemployment Rate (FRED)', '%', 'macroeconomic');

-- Insert data sources
INSERT INTO sources (source_name, source_url, api_endpoint, update_frequency) VALUES
('IMF', 'https://www.imf.org', 'http://dataservices.imf.org/REST/SDMX_JSON.svc/', 'quarterly'),
('World Bank', 'https://www.worldbank.org', 'https://api.worldbank.org/v2/', 'annual'),
('OECD', 'https://www.oecd.org', 'https://stats.oecd.org/SDMX-JSON/data/', 'quarterly'),
('FRED', 'https://fred.stlouisfed.org', 'https://api.stlouisfed.org/fred/', 'monthly');

-- Create a view for easy querying
CREATE OR REPLACE VIEW v_observations AS
SELECT
    c.country_code,
    c.country_name,
    i.indicator_code,
    i.indicator_name,
    i.unit,
    s.source_name,
    o.time_period,
    o.value,
    o.frequency,
    o.status
FROM observations o
JOIN countries c ON o.country_code = c.country_code
JOIN indicators i ON o.indicator_id = i.indicator_id
JOIN sources s ON o.source_id = s.source_id;

-- Grant permissions (adjust as needed)
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO archimedes_app;

-- Sample queries for testing

-- Get latest GDP data for all G20 countries
-- SELECT * FROM v_observations
-- WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG'
--   AND time_period >= '2020-01-01'
-- ORDER BY country_name, time_period DESC;

-- Compare unemployment across countries
-- SELECT country_name, time_period, value
-- FROM v_observations
-- WHERE indicator_code = 'SL.UEM.TOTL.ZS'
--   AND EXTRACT(YEAR FROM time_period) = 2023
-- ORDER BY value DESC;
