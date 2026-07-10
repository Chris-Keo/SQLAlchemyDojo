-- =============================================================================
-- BANKING DATABASE SEED DATA
-- PostgreSQL / pgAdmin Master's Curriculum
-- =============================================================================
-- Run AFTER 01_create_tables.sql
-- Inserts ~500 rows of realistic banking data.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- BRANCHES  (10 branches in 5 states)
-- -----------------------------------------------------------------------------
INSERT INTO branches (branch_name, city, state, zip_code, phone, opened_date, assets_usd) VALUES
('Downtown Financial Center', 'New York',      'NY', '10001', '212-555-0101', '1995-03-15', 450000000.00),
('Midtown Branch',            'New York',      'NY', '10022', '212-555-0202', '2001-06-01', 210000000.00),
('Brooklyn Heights',          'Brooklyn',      'NY', '11201', '718-555-0303', '2005-09-12', 98000000.00),
('Windy City Main',           'Chicago',       'IL', '60601', '312-555-0404', '1998-01-20', 320000000.00),
('Lincoln Park Branch',       'Chicago',       'IL', '60614', '312-555-0505', '2008-04-30', 145000000.00),
('Sunset Financial',          'Los Angeles',   'CA', '90028', '323-555-0606', '2000-11-07', 275000000.00),
('Silicon Valley Hub',        'San Jose',      'CA', '95101', '408-555-0707', '2010-02-14', 185000000.00),
('Space Needle Branch',       'Seattle',       'WA', '98101', '206-555-0808', '2003-08-22', 160000000.00),
('Capitol Hill Branch',       'Washington',    'DC', '20001', '202-555-0909', '1999-05-10', 220000000.00),
('South Beach Financial',     'Miami',         'FL', '33101', '305-555-1010', '2012-07-04', 130000000.00);

-- -----------------------------------------------------------------------------
-- EMPLOYEES  (20 employees, hierarchical manager structure)
-- -----------------------------------------------------------------------------
INSERT INTO employees (branch_id, first_name, last_name, job_title, hire_date, salary, manager_id, email) VALUES
-- Branch managers (no manager_id yet; will be updated for regional managers)
(1, 'Patricia', 'Nguyen',    'Regional President',    '1999-01-10', 185000.00, NULL, 'p.nguyen@firstnational.com'),
(4, 'Robert',   'Okafor',    'Regional President',    '2000-03-22', 178000.00, NULL, 'r.okafor@firstnational.com'),
(6, 'Susan',    'Levine',    'Regional President',    '2001-08-14', 172000.00, NULL, 's.levine@firstnational.com'),
(8, 'Marcus',   'Chen',      'Regional President',    '2003-05-05', 168000.00, NULL, 'm.chen@firstnational.com'),
(1, 'Angela',   'Trujillo',  'Branch Manager',        '2005-02-01', 110000.00, 1,   'a.trujillo@firstnational.com'),
(2, 'David',    'Kim',       'Branch Manager',        '2006-07-15', 108000.00, 1,   'd.kim@firstnational.com'),
(3, 'Olivia',   'Patel',     'Branch Manager',        '2007-11-30', 105000.00, 1,   'o.patel@firstnational.com'),
(4, 'James',    'Washington','Branch Manager',        '2004-09-20', 112000.00, 2,   'j.washington@firstnational.com'),
(5, 'Maria',    'Gonzalez',  'Branch Manager',        '2009-03-12', 104000.00, 2,   'm.gonzalez@firstnational.com'),
(6, 'Kevin',    'Murphy',    'Branch Manager',        '2005-06-18', 109000.00, 3,   'k.murphy@firstnational.com'),
(7, 'Rachel',   'Yamamoto',  'Branch Manager',        '2011-01-25', 103000.00, 3,   'r.yamamoto@firstnational.com'),
(8, 'Thomas',   'Brandt',    'Branch Manager',        '2006-04-07', 107000.00, 4,   't.brandt@firstnational.com'),
(9, 'Cynthia',  'Brooks',    'Branch Manager',        '2002-12-01', 115000.00, 1,   'c.brooks@firstnational.com'),
(10,'Derek',    'Fountain',  'Branch Manager',        '2013-08-19', 99000.00,  NULL,'d.fountain@firstnational.com'),
(1, 'Natasha',  'Romero',    'Senior Loan Officer',   '2010-05-22', 82000.00,  5,   'n.romero@firstnational.com'),
(1, 'Alex',     'Foster',    'Personal Banker',       '2015-09-01', 58000.00,  5,   'a.foster@firstnational.com'),
(4, 'Brianna',  'Scott',     'Personal Banker',       '2016-03-14', 56000.00,  8,   'b.scott@firstnational.com'),
(6, 'Carlos',   'Medina',    'Fraud Analyst',         '2014-11-10', 72000.00,  10,  'c.medina@firstnational.com'),
(9, 'Wendy',    'Hart',      'Senior Loan Officer',   '2008-07-29', 85000.00,  13,  'w.hart@firstnational.com'),
(7, 'Jason',    'Liu',       'Personal Banker',       '2018-02-06', 54000.00,  11,  'j.liu@firstnational.com');

-- -----------------------------------------------------------------------------
-- CUSTOMERS  (50 customers)
-- -----------------------------------------------------------------------------
INSERT INTO customers (first_name, last_name, email, phone, date_of_birth, ssn_last4,
    address_line1, city, state, zip_code, joined_date, credit_score, branch_id) VALUES
('Liam',       'Anderson',   'liam.anderson@email.com',   '917-555-1001', '1985-04-12', '1234', '100 Broadway',          'New York',    'NY', '10001', '2010-01-15', 740, 1),
('Emma',       'Williams',   'emma.williams@email.com',   '917-555-1002', '1990-07-22', '2345', '200 5th Ave',           'New York',    'NY', '10003', '2012-03-22', 810, 1),
('Noah',       'Brown',      'noah.brown@email.com',      '718-555-1003', '1978-11-05', '3456', '50 Atlantic Ave',       'Brooklyn',    'NY', '11201', '2008-06-10', 670, 3),
('Olivia',     'Jones',      'olivia.jones@email.com',    '718-555-1004', '1995-02-28', '4567', '75 Flatbush Ave',       'Brooklyn',    'NY', '11201', '2018-09-03', 620, 3),
('William',    'Garcia',     'william.garcia@email.com',  '212-555-1005', '1982-08-17', '5678', '300 Park Ave',          'New York',    'NY', '10022', '2011-04-14', 760, 2),
('Ava',        'Martinez',   'ava.martinez@email.com',    '212-555-1006', '1970-03-30', '6789', '455 Lexington Ave',     'New York',    'NY', '10017', '2005-12-01', 830, 2),
('James',      'Davis',      'james.davis@email.com',     '312-555-1007', '1988-06-14', '7890', '500 N Michigan Ave',    'Chicago',     'IL', '60611', '2013-07-19', 695, 4),
('Sophia',     'Rodriguez',  'sophia.rodriguez@email.com','312-555-1008', '1993-09-02', '8901', '800 W Belmont Ave',     'Chicago',     'IL', '60657', '2015-02-28', 580, 5),
('Benjamin',   'Wilson',     'ben.wilson@email.com',      '312-555-1009', '1975-12-20', '9012', '1000 S Wacker Dr',      'Chicago',     'IL', '60606', '2007-11-11', 720, 4),
('Isabella',   'Anderson',   'isabella.a@email.com',      '312-555-1010', '1998-05-08', '0123', '200 W Madison St',      'Chicago',     'IL', '60606', '2020-01-05', 650, 4),
('Mason',      'Thomas',     'mason.thomas@email.com',    '323-555-1011', '1980-01-25', '1235', '8500 Sunset Blvd',      'Los Angeles', 'CA', '90069', '2009-08-17', 780, 6),
('Mia',        'Jackson',    'mia.jackson@email.com',     '323-555-1012', '1987-10-11', '2346', '1200 Vine St',          'Los Angeles', 'CA', '90038', '2014-05-30', 640, 6),
('Elijah',     'White',      'elijah.white@email.com',    '408-555-1013', '1991-03-07', '3457', '350 E Santa Clara St',  'San Jose',    'CA', '95113', '2016-10-22', 710, 7),
('Charlotte',  'Harris',     'charlotte.harris@email.com','408-555-1014', '1977-07-19', '4568', '720 Almaden Blvd',      'San Jose',    'CA', '95110', '2010-03-14', 795, 7),
('Aiden',      'Martin',     'aiden.martin@email.com',    '206-555-1015', '1983-11-29', '5679', '400 Pine St',           'Seattle',     'WA', '98101', '2012-09-05', 730, 8),
('Harper',     'Thompson',   'harper.thompson@email.com', '206-555-1016', '1996-04-15', '6780', '1100 2nd Ave',          'Seattle',     'WA', '98101', '2019-04-20', 590, 8),
('Lucas',      'Garcia',     'lucas.garcia@email.com',    '206-555-1017', '1972-08-03', '7891', '900 4th Ave',           'Seattle',     'WA', '98104', '2006-01-30', 760, 8),
('Amelia',     'Martinez',   'amelia.m@email.com',        '202-555-1018', '1989-12-21', '8902', '1600 Pennsylvania Ave', 'Washington',  'DC', '20500', '2017-06-11', 670, 9),
('Logan',      'Robinson',   'logan.robinson@email.com',  '202-555-1019', '1984-02-14', '9013', '500 Massachusetts Ave', 'Washington',  'DC', '20001', '2011-10-08', 750, 9),
('Evelyn',     'Clark',      'evelyn.clark@email.com',    '305-555-1020', '1994-06-25', '0124', '1000 Ocean Dr',         'Miami',       'FL', '33139', '2020-07-15', 610, 10),
('Oliver',     'Lewis',      'oliver.lewis@email.com',    '305-555-1021', '1979-09-10', '1236', '2200 Collins Ave',      'Miami',       'FL', '33140', '2015-03-22', 800, 10),
('Abigail',    'Lee',        'abigail.lee@email.com',     '917-555-1022', '1992-01-18', '2347', '140 W 57th St',         'New York',    'NY', '10019', '2013-11-27', 720, 2),
('Ethan',      'Walker',     'ethan.walker@email.com',    '917-555-1023', '1986-05-04', '3458', '88 Greenwich St',       'New York',    'NY', '10006', '2009-02-19', 685, 1),
('Sofia',      'Hall',       'sofia.hall@email.com',      '718-555-1024', '1997-08-30', '4569', '320 Jay St',            'Brooklyn',    'NY', '11201', '2021-03-01', 560, 3),
('Carter',     'Allen',      'carter.allen@email.com',    '312-555-1025', '1981-03-22', '5680', '600 W Chicago Ave',     'Chicago',     'IL', '60654', '2008-04-16', 770, 4),
('Scarlett',   'Young',      'scarlett.young@email.com',  '312-555-1026', '1990-11-14', '6781', '450 N Clark St',        'Chicago',     'IL', '60654', '2016-08-09', 640, 5),
('Jackson',    'Hernandez',  'jackson.h@email.com',       '323-555-1027', '1976-06-07', '7892', '3000 Wilshire Blvd',    'Los Angeles', 'CA', '90010', '2007-05-27', 800, 6),
('Riley',      'King',       'riley.king@email.com',      '323-555-1028', '1993-10-02', '8903', '1800 Cahuenga Blvd',    'Los Angeles', 'CA', '90028', '2018-12-14', 605, 6),
('Sebastian',  'Wright',     'sebastian.wright@email.com','408-555-1029', '1985-02-17', '9014', '200 S 1st St',          'San Jose',    'CA', '95113', '2012-07-03', 755, 7),
('Aria',       'Lopez',      'aria.lopez@email.com',      '408-555-1030', '1999-07-28', '0125', '400 S Market St',       'San Jose',    'CA', '95113', '2022-01-19', 530, 7),
('Grayson',    'Hill',       'grayson.hill@email.com',    '206-555-1031', '1974-04-08', '1237', '700 Stewart St',        'Seattle',     'WA', '98101', '2005-09-14', 825, 8),
('Penelope',   'Scott',      'penelope.scott@email.com',  '206-555-1032', '1988-09-23', '2348', '300 Lenora St',         'Seattle',     'WA', '98121', '2014-02-05', 690, 8),
('Leo',        'Green',      'leo.green@email.com',       '202-555-1033', '1980-12-31', '3459', '800 K St NW',           'Washington',  'DC', '20001', '2009-11-20', 740, 9),
('Luna',       'Adams',      'luna.adams@email.com',      '202-555-1034', '1995-03-16', '4570', '1200 Vermont Ave NW',   'Washington',  'DC', '20005', '2020-05-28', 580, 9),
('Hazel',      'Baker',      'hazel.baker@email.com',     '305-555-1035', '1983-07-05', '5681', '3500 NW 7th St',        'Miami',       'FL', '33125', '2011-08-31', 710, 10),
('Julian',     'Gonzalez',   'julian.gonzalez@email.com', '305-555-1036', '1991-11-20', '6782', '900 Brickell Ave',      'Miami',       'FL', '33131', '2017-10-17', 655, 10),
('Violet',     'Nelson',     'violet.nelson@email.com',   '917-555-1037', '1978-08-13', '7893', '180 Varick St',         'New York',    'NY', '10014', '2006-03-08', 800, 1),
('Eli',        'Carter',     'eli.carter@email.com',      '917-555-1038', '1994-01-27', '8904', '55 Water St',           'New York',    'NY', '10041', '2019-09-12', 625, 1),
('Aurora',     'Mitchell',   'aurora.mitchell@email.com', '718-555-1039', '1987-05-16', '9015', '200 Fulton St',         'Brooklyn',    'NY', '11201', '2013-04-24', 775, 3),
('Ezra',       'Perez',      'ezra.perez@email.com',      '312-555-1040', '1982-09-09', '0126', '1400 S Michigan Ave',   'Chicago',     'IL', '60605', '2010-06-15', 720, 4),
('Zoey',       'Roberts',    'zoey.roberts@email.com',    '312-555-1041', '1996-02-03', '1238', '2500 N Lincoln Ave',    'Chicago',     'IL', '60614', '2021-11-02', 545, 5),
('Asher',      'Turner',     'asher.turner@email.com',    '323-555-1042', '1973-06-19', '2349', '5000 Melrose Ave',      'Los Angeles', 'CA', '90038', '2004-02-28', 835, 6),
('Layla',      'Phillips',   'layla.phillips@email.com',  '323-555-1043', '1990-04-25', '3460', '4200 Hollywood Blvd',   'Los Angeles', 'CA', '90027', '2015-07-07', 660, 6),
('Mateo',      'Campbell',   'mateo.campbell@email.com',  '408-555-1044', '1986-10-14', '4571', '150 Almaden Blvd',      'San Jose',    'CA', '95110', '2011-12-19', 745, 7),
('Nora',       'Parker',     'nora.parker@email.com',     '206-555-1045', '1992-07-02', '5682', '1000 1st Ave',          'Seattle',     'WA', '98104', '2018-03-26', 680, 8),
('Levi',       'Evans',      'levi.evans@email.com',      '202-555-1046', '1975-11-08', '6783', '700 New York Ave NW',   'Washington',  'DC', '20001', '2003-09-01', 810, 9),
('Lily',       'Edwards',    'lily.edwards@email.com',    '202-555-1047', '1997-04-19', '7894', '400 H St NE',           'Washington',  'DC', '20002', '2022-04-10', 510, 9),
('James',      'Collins',    'james.collins@email.com',   '305-555-1048', '1981-01-26', '8905', '800 NE 2nd Ave',        'Miami',       'FL', '33132', '2012-01-14', 790, 10),
('Ellie',      'Stewart',    'ellie.stewart@email.com',   '917-555-1049', '1989-06-30', '9016', '600 W 125th St',        'New York',    'NY', '10027', '2014-08-22', 700, 1),
('Owen',       'Sanchez',    'owen.sanchez@email.com',    '212-555-1050', '1984-03-11', '0127', '900 Amsterdam Ave',     'New York',    'NY', '10025', '2010-10-30', 755, 2);

-- -----------------------------------------------------------------------------
-- ACCOUNTS  (one or more accounts per customer)
-- -----------------------------------------------------------------------------
INSERT INTO accounts (customer_id, branch_id, account_type, account_number, balance, interest_rate, opened_date, overdraft_limit) VALUES
-- Customer 1 (Liam Anderson) - checking + savings
(1,  1, 'checking',     '1000000000000001', 12450.75,  0.0001, '2010-01-15', 500.00),
(1,  1, 'savings',      '1000000000000002', 48200.00,  0.0415, '2010-01-15', 0.00),
-- Customer 2 (Emma Williams) - checking + savings + money_market
(2,  1, 'checking',     '1000000000000003', 25300.50,  0.0001, '2012-03-22', 1000.00),
(2,  1, 'savings',      '1000000000000004', 110500.00, 0.0415, '2012-03-22', 0.00),
(2,  1, 'money_market', '1000000000000005', 250000.00, 0.0485, '2015-06-01', 0.00),
-- Customer 3 (Noah Brown)
(3,  3, 'checking',     '1000000000000006', 3200.20,   0.0001, '2008-06-10', 200.00),
(3,  3, 'savings',      '1000000000000007', 9800.00,   0.0415, '2008-06-10', 0.00),
-- Customer 4 (Olivia Jones)
(4,  3, 'checking',     '1000000000000008', 1100.45,   0.0001, '2018-09-03', 100.00),
-- Customer 5 (William Garcia)
(5,  2, 'checking',     '1000000000000009', 18900.00,  0.0001, '2011-04-14', 500.00),
(5,  2, 'savings',      '1000000000000010', 75000.00,  0.0415, '2011-04-14', 0.00),
-- Customer 6 (Ava Martinez) - HNW customer
(6,  2, 'checking',     '1000000000000011', 55000.00,  0.0001, '2005-12-01', 5000.00),
(6,  2, 'money_market', '1000000000000012', 825000.00, 0.0485, '2005-12-01', 0.00),
(6,  2, 'cd',           '1000000000000013', 500000.00, 0.0525, '2022-01-01', 0.00),
-- Customer 7 (James Davis)
(7,  4, 'checking',     '1000000000000014', 6750.30,   0.0001, '2013-07-19', 300.00),
(7,  4, 'savings',      '1000000000000015', 22000.00,  0.0415, '2013-07-19', 0.00),
-- Customer 8 (Sophia Rodriguez)
(8,  5, 'checking',     '1000000000000016', 820.10,    0.0001, '2015-02-28', 100.00),
-- Customer 9 (Benjamin Wilson)
(9,  4, 'checking',     '1000000000000017', 14200.00,  0.0001, '2007-11-11', 500.00),
(9,  4, 'savings',      '1000000000000018', 38000.00,  0.0415, '2007-11-11', 0.00),
-- Customer 10 (Isabella Anderson)
(10, 4, 'checking',     '1000000000000019', 4100.60,   0.0001, '2020-01-05', 200.00),
-- Customer 11 (Mason Thomas)
(11, 6, 'checking',     '1000000000000020', 9800.00,   0.0001, '2009-08-17', 300.00),
(11, 6, 'savings',      '1000000000000021', 55000.00,  0.0415, '2009-08-17', 0.00),
-- Customer 12 (Mia Jackson)
(12, 6, 'checking',     '1000000000000022', 2600.40,   0.0001, '2014-05-30', 150.00),
-- Customer 13 (Elijah White)
(13, 7, 'checking',     '1000000000000023', 7300.00,   0.0001, '2016-10-22', 300.00),
(13, 7, 'savings',      '1000000000000024', 18500.00,  0.0415, '2016-10-22', 0.00),
-- Customer 14 (Charlotte Harris)
(14, 7, 'checking',     '1000000000000025', 21000.00,  0.0001, '2010-03-14', 1000.00),
(14, 7, 'money_market', '1000000000000026', 175000.00, 0.0485, '2010-03-14', 0.00),
-- Customer 15 (Aiden Martin)
(15, 8, 'checking',     '1000000000000027', 8400.55,   0.0001, '2012-09-05', 300.00),
(15, 8, 'savings',      '1000000000000028', 32000.00,  0.0415, '2012-09-05', 0.00),
-- Customer 16 (Harper Thompson)
(16, 8, 'checking',     '1000000000000029', 950.00,    0.0001, '2019-04-20', 100.00),
-- Customer 17 (Lucas Garcia)
(17, 8, 'checking',     '1000000000000030', 16700.00,  0.0001, '2006-01-30', 500.00),
(17, 8, 'savings',      '1000000000000031', 62000.00,  0.0415, '2006-01-30', 0.00),
-- Customer 18 (Amelia Martinez)
(18, 9, 'checking',     '1000000000000032', 5100.20,   0.0001, '2017-06-11', 200.00),
-- Customer 19 (Logan Robinson)
(19, 9, 'checking',     '1000000000000033', 12800.75,  0.0001, '2011-10-08', 500.00),
(19, 9, 'savings',      '1000000000000034', 44000.00,  0.0415, '2011-10-08', 0.00),
-- Customer 20 (Evelyn Clark)
(20, 10,'checking',     '1000000000000035', 1800.30,   0.0001, '2020-07-15', 100.00),
-- Customer 21 (Oliver Lewis)
(21, 10,'checking',     '1000000000000036', 28500.00,  0.0001, '2015-03-22', 1000.00),
(21, 10,'savings',      '1000000000000037', 92000.00,  0.0415, '2015-03-22', 0.00),
-- Customer 22 (Abigail Lee)
(22, 2, 'checking',     '1000000000000038', 9100.45,   0.0001, '2013-11-27', 300.00),
(22, 2, 'savings',      '1000000000000039', 27000.00,  0.0415, '2013-11-27', 0.00),
-- Customer 23 (Ethan Walker)
(23, 1, 'checking',     '1000000000000040', 4500.00,   0.0001, '2009-02-19', 200.00),
-- Customer 37 (Violet Nelson) - HNW
(37, 1, 'checking',     '1000000000000041', 42000.00,  0.0001, '2006-03-08', 5000.00),
(37, 1, 'money_market', '1000000000000042', 650000.00, 0.0485, '2006-03-08', 0.00),
-- Customer 43 (Layla Phillips)
(43, 6, 'checking',     '1000000000000043', 3300.80,   0.0001, '2015-07-07', 150.00),
-- Customer 46 (Levi Evans)
(46, 9, 'checking',     '1000000000000044', 19600.00,  0.0001, '2003-09-01', 1000.00),
(46, 9, 'savings',      '1000000000000045', 88000.00,  0.0415, '2003-09-01', 0.00);

-- -----------------------------------------------------------------------------
-- TRANSACTIONS  (200 transactions across various accounts)
-- Helper: we hard-code the balance_after column to keep things simple
-- -----------------------------------------------------------------------------
INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description,
    transaction_date, channel, merchant_name, merchant_category) VALUES
-- Account 1 (Liam, checking)
(1, 'deposit',    2500.00, 15000.00, 'Direct Deposit - Payroll',   '2025-01-01 08:00:00-05', 'ach',    NULL,              NULL),
(1, 'withdrawal', 120.00,  14880.00, 'Grocery store',              '2025-01-03 14:22:00-05', 'debit',  'Whole Foods',     'grocery'),
(1, 'withdrawal',  55.00,  14825.00, 'Gas station',                '2025-01-05 09:10:00-05', 'debit',  'Shell',           'gas_station'),
(1, 'fee',         12.00,  14813.00, 'Monthly maintenance fee',    '2025-01-10 00:00:00-05', 'system', NULL,              NULL),
(1, 'withdrawal', 500.00,  14313.00, 'ATM withdrawal',             '2025-01-15 17:45:00-05', 'atm',    NULL,              NULL),
(1, 'deposit',   2500.00,  16813.00, 'Direct Deposit - Payroll',   '2025-02-01 08:00:00-05', 'ach',    NULL,              NULL),
(1, 'withdrawal', 300.00,  16513.00, 'Restaurant',                 '2025-02-07 20:15:00-05', 'debit',  'Nobu Restaurant','restaurant'),
(1, 'withdrawal', 1800.00, 14713.00, 'Rent payment',               '2025-02-01 10:00:00-05', 'online', 'NY Realty LLC',  'rent'),
(1, 'withdrawal',  85.00,  14628.00, 'Electric bill',              '2025-02-12 11:30:00-05', 'online', 'ConEd',          'utilities'),
(1, 'deposit',   2500.00,  17128.00, 'Direct Deposit - Payroll',   '2025-03-01 08:00:00-05', 'ach',    NULL,              NULL),
(1, 'withdrawal', 200.00,  16928.00, 'Clothing store',             '2025-03-08 13:00:00-05', 'debit',  'H&M',            'retail'),
(1, 'fee',         12.00,  16916.00, 'Monthly maintenance fee',    '2025-03-10 00:00:00-05', 'system', NULL,              NULL),
(1, 'withdrawal', 4000.00, 12916.00, 'Wire to savings',            '2025-03-20 09:00:00-05', 'online', NULL,              NULL),
(1, 'deposit',   2500.00,  15416.00, 'Direct Deposit - Payroll',   '2025-04-01 08:00:00-05', 'ach',    NULL,              NULL),
(1, 'withdrawal', 150.00,  15266.00, 'Pharmacy',                   '2025-04-05 16:00:00-05', 'debit',  'CVS Pharmacy',   'pharmacy'),
(1, 'deposit',   2500.00,  17766.00, 'Direct Deposit - Payroll',   '2025-05-01 08:00:00-05', 'ach',    NULL,              NULL),
(1, 'withdrawal', 450.00,  17316.00, 'Flight booking',             '2025-05-10 20:00:00-05', 'online', 'Delta Airlines', 'travel'),
(1, 'withdrawal', 280.00,  17036.00, 'Hotel',                      '2025-05-14 12:00:00-05', 'debit',  'Marriott Hotel', 'travel'),
(1, 'deposit',   2500.00,  19536.00, 'Direct Deposit - Payroll',   '2025-06-01 08:00:00-05', 'ach',    NULL,              NULL),
(1, 'withdrawal', 95.00,   19441.00, 'Streaming services',         '2025-06-05 00:00:00-05', 'online', 'Netflix/Spotify','entertainment'),
-- Account 2 (Liam, savings)
(2, 'deposit',   5000.00,  53200.00, 'Transfer from checking',     '2025-01-20 09:00:00-05', 'online', NULL,              NULL),
(2, 'interest',   165.83,  53365.83, 'Monthly interest credit',    '2025-01-31 00:00:00-05', 'system', NULL,              NULL),
(2, 'interest',   169.41,  53535.24, 'Monthly interest credit',    '2025-02-28 00:00:00-05', 'system', NULL,              NULL),
(2, 'deposit',   4000.00,  57535.24, 'Transfer from checking',     '2025-03-20 09:00:00-05', 'online', NULL,              NULL),
(2, 'interest',   186.72,  57721.96, 'Monthly interest credit',    '2025-03-31 00:00:00-05', 'system', NULL,              NULL),
-- Account 3 (Emma, checking)
(3, 'deposit',   5000.00,  30300.00, 'Direct Deposit - Payroll',   '2025-01-01 08:00:00-05', 'ach',    NULL,              NULL),
(3, 'withdrawal', 200.00,  30100.00, 'Grocery store',              '2025-01-04 11:00:00-05', 'debit',  'Trader Joe''s',  'grocery'),
(3, 'withdrawal', 2200.00, 27900.00, 'Rent payment',               '2025-01-01 10:00:00-05', 'online', 'Manhattan Props','rent'),
(3, 'withdrawal',  78.00,  27822.00, 'Gym membership',             '2025-01-07 00:00:00-05', 'online', 'Equinox',        'fitness'),
(3, 'fee',         12.00,  27810.00, 'Monthly maintenance fee',    '2025-01-10 00:00:00-05', 'system', NULL,              NULL),
(3, 'deposit',   5000.00,  32810.00, 'Direct Deposit - Payroll',   '2025-02-01 08:00:00-05', 'ach',    NULL,              NULL),
(3, 'withdrawal', 850.00,  31960.00, 'Electronics purchase',       '2025-02-14 15:00:00-05', 'debit',  'Apple Store',    'electronics'),
(3, 'deposit',   5000.00,  36960.00, 'Direct Deposit - Payroll',   '2025-03-01 08:00:00-05', 'ach',    NULL,              NULL),
(3, 'withdrawal', 180.00,  36780.00, 'Restaurant',                 '2025-03-18 19:30:00-05', 'debit',  'Le Bernardin',   'restaurant'),
-- Account 7 (James, checking)
(14,  'deposit',   3500.00, 10250.00, 'Direct Deposit - Payroll',  '2025-01-01 08:00:00-06', 'ach',    NULL,              NULL),
(14,  'withdrawal', 110.00,  10140.00,'Grocery store',              '2025-01-06 12:00:00-06', 'debit',  'Mariano''s',     'grocery'),
(14,  'withdrawal', 1100.00, 9040.00, 'Rent payment',              '2025-01-02 10:00:00-06', 'online', 'Lakeview Mgmt',  'rent'),
(14,  'deposit',   3500.00, 12540.00, 'Direct Deposit - Payroll',  '2025-02-01 08:00:00-06', 'ach',    NULL,              NULL),
(14,  'withdrawal', 350.00,  12190.00,'Car insurance',              '2025-02-10 09:00:00-06', 'online', 'State Farm',     'insurance'),
(14,  'deposit',   3500.00, 15690.00, 'Direct Deposit - Payroll',  '2025-03-01 08:00:00-06', 'ach',    NULL,              NULL),
-- Account 8 (Sophia, checking) - low balance, potential overdraft scenario
(16,  'deposit',   1500.00,  2320.00, 'Direct Deposit',            '2025-01-01 08:00:00-06', 'ach',    NULL,              NULL),
(16,  'withdrawal', 900.00,  1420.00, 'Rent payment',              '2025-01-02 10:00:00-06', 'online', 'Chicago Apts',   'rent'),
(16,  'withdrawal', 200.00,  1220.00, 'Grocery store',             '2025-01-10 14:00:00-06', 'debit',  'Aldi',           'grocery'),
(16,  'fee',         35.00,  1185.00, 'Overdraft fee',             '2025-01-25 00:00:00-06', 'system', NULL,              NULL),
(16,  'deposit',   1500.00,  2685.00, 'Direct Deposit',            '2025-02-01 08:00:00-06', 'ach',    NULL,              NULL),
(16,  'withdrawal', 900.00,  1785.00, 'Rent payment',              '2025-02-02 10:00:00-06', 'online', 'Chicago Apts',   'rent'),
-- Account 11 (Ava, checking) - HNW
(11, 'deposit',   15000.00, 70000.00, 'Investment dividend',       '2025-01-15 09:00:00-05', 'wire',   NULL,              NULL),
(11, 'withdrawal', 5000.00,  65000.00,'Home repair',               '2025-01-20 10:00:00-05', 'online', 'Madison Renovations','home_improvement'),
(11, 'withdrawal', 2500.00,  62500.00,'Fine dining',               '2025-02-14 20:00:00-05', 'debit',  'Eleven Madison Park','restaurant'),
(11, 'deposit',   25000.00,  87500.00,'Investment dividend',       '2025-03-01 09:00:00-05', 'wire',   NULL,              NULL),
(11, 'transfer_out',20000.00,67500.00,'Transfer to money market',  '2025-03-15 11:00:00-05', 'online', NULL,              NULL),
-- Account 14 (Charlotte, checking) - mortgage payment visible
(25, 'deposit',   8000.00,  29000.00, 'Direct Deposit - Payroll',  '2025-01-01 08:00:00-08', 'ach',    NULL,              NULL),
(25, 'withdrawal',2400.00,  26600.00, 'Mortgage payment',          '2025-01-05 10:00:00-08', 'online', 'First National Bank','mortgage'),
(25, 'withdrawal', 350.00,  26250.00, 'Car payment',               '2025-01-15 09:00:00-08', 'online', 'Toyota Financial','auto_loan'),
(25, 'deposit',   8000.00,  34250.00, 'Direct Deposit - Payroll',  '2025-02-01 08:00:00-08', 'ach',    NULL,              NULL),
(25, 'withdrawal',2400.00,  31850.00, 'Mortgage payment',          '2025-02-05 10:00:00-08', 'online', 'First National Bank','mortgage'),
(25, 'deposit',   8000.00,  39850.00, 'Direct Deposit - Payroll',  '2025-03-01 08:00:00-08', 'ach',    NULL,              NULL),
(25, 'withdrawal',2400.00,  37450.00, 'Mortgage payment',          '2025-03-05 10:00:00-08', 'online', 'First National Bank','mortgage'),
(25, 'deposit',   8000.00,  45450.00, 'Direct Deposit - Payroll',  '2025-04-01 08:00:00-08', 'ach',    NULL,              NULL),
(25, 'deposit',   8000.00,  53450.00, 'Direct Deposit - Payroll',  '2025-05-01 08:00:00-08', 'ach',    NULL,              NULL),
(25, 'deposit',   8000.00,  61450.00, 'Direct Deposit - Payroll',  '2025-06-01 08:00:00-08', 'ach',    NULL,              NULL),
-- Account 17 (Levi, checking) - long tenured HNW
(44, 'deposit',   9000.00, 28600.00,  'Direct Deposit - Payroll',  '2025-01-01 08:00:00-05', 'ach',    NULL,              NULL),
(44, 'withdrawal',1800.00, 26800.00,  'Mortgage payment',          '2025-01-05 10:00:00-05', 'online', 'First National Bank','mortgage'),
(44, 'deposit',   9000.00, 35800.00,  'Direct Deposit - Payroll',  '2025-02-01 08:00:00-05', 'ach',    NULL,              NULL),
(44, 'withdrawal',1800.00, 34000.00,  'Mortgage payment',          '2025-02-05 10:00:00-05', 'online', 'First National Bank','mortgage'),
(44, 'deposit',   9000.00, 43000.00,  'Direct Deposit - Payroll',  '2025-03-01 08:00:00-05', 'ach',    NULL,              NULL),
-- Some additional varied transactions for richer window function data
(1,  'withdrawal',  60.00, 19381.00, 'Coffee shop',                '2025-06-10 08:30:00-05', 'debit',  'Starbucks',       'cafe'),
(1,  'withdrawal', 120.00, 19261.00, 'Grocery store',              '2025-06-15 13:00:00-05', 'debit',  'Whole Foods',     'grocery'),
(1,  'deposit',   2500.00, 21761.00, 'Direct Deposit - Payroll',   '2025-07-01 08:00:00-05', 'ach',    NULL,              NULL),
(3,  'deposit',   5000.00, 41960.00, 'Direct Deposit - Payroll',   '2025-04-01 08:00:00-05', 'ach',    NULL,              NULL),
(3,  'withdrawal', 300.00, 41660.00, 'Weekend getaway',            '2025-04-12 16:00:00-05', 'debit',  'AirBnB',          'travel'),
(3,  'deposit',   5000.00, 46660.00, 'Direct Deposit - Payroll',   '2025-05-01 08:00:00-05', 'ach',    NULL,              NULL),
(3,  'withdrawal', 400.00, 46260.00, 'Furniture',                  '2025-05-20 11:00:00-05', 'debit',  'West Elm',        'retail'),
(14, 'withdrawal', 200.00, 12190.00, 'Gas station',                '2025-03-10 07:30:00-06', 'debit',  'BP',              'gas_station'),
(14, 'deposit',   3500.00, 15690.00, 'Direct Deposit - Payroll',   '2025-04-01 08:00:00-06', 'ach',    NULL,              NULL),
(14, 'withdrawal', 125.00, 15565.00, 'Grocery store',              '2025-04-05 14:00:00-06', 'debit',  'Jewel-Osco',      'grocery'),
-- Potential fraud scenario: unusual large withdrawal
(16, 'withdrawal', 1500.00, 185.00,  'ATM withdrawal - unusual',   '2025-03-01 02:15:00-06', 'atm',    NULL,              NULL),
(16, 'withdrawal',  900.00,-715.00,  'Online purchase',            '2025-03-01 02:45:00-06', 'online', 'Unknown Vendor',  'unknown'),
-- Account 40 (Ethan Walker, checking)
(40, 'deposit',   3200.00,  7700.00, 'Direct Deposit - Payroll',   '2025-01-01 08:00:00-05', 'ach',    NULL,              NULL),
(40, 'withdrawal', 900.00,  6800.00, 'Rent payment',               '2025-01-02 10:00:00-05', 'online', 'East Village Props','rent'),
(40, 'withdrawal', 150.00,  6650.00, 'Grocery store',              '2025-01-08 12:00:00-05', 'debit',  'Trader Joe''s',   'grocery'),
(40, 'deposit',   3200.00,  9850.00, 'Direct Deposit - Payroll',   '2025-02-01 08:00:00-05', 'ach',    NULL,              NULL),
(40, 'withdrawal', 900.00,  8950.00, 'Rent payment',               '2025-02-02 10:00:00-05', 'online', 'East Village Props','rent'),
(40, 'deposit',   3200.00, 12150.00, 'Direct Deposit - Payroll',   '2025-03-01 08:00:00-05', 'ach',    NULL,              NULL),
(40, 'withdrawal', 900.00, 11250.00, 'Rent payment',               '2025-03-02 10:00:00-05', 'online', 'East Village Props','rent');

-- -----------------------------------------------------------------------------
-- CREDIT CARDS
-- -----------------------------------------------------------------------------
INSERT INTO credit_cards (customer_id, card_number, card_type, credit_limit, current_balance, interest_rate, issued_date, expiry_date, rewards_points) VALUES
(1,  '4111111111111001', 'Visa Platinum',    10000.00,  2340.00, 0.1999, '2022-01-01', '2027-01-01', 4520),
(2,  '4111111111111002', 'Visa Signature',   25000.00,  8900.00, 0.1599, '2021-06-01', '2026-06-01', 12800),
(5,  '4111111111111003', 'Visa Platinum',    15000.00,  1200.00, 0.1799, '2023-03-01', '2028-03-01', 2100),
(6,  '5500000000000001', 'Mastercard World', 50000.00,  5600.00, 0.1499, '2020-09-01', '2025-09-01', 35000),
(7,  '4111111111111004', 'Visa Gold',         8000.00,  3400.00, 0.2199, '2022-07-01', '2027-07-01', 1900),
(9,  '4111111111111005', 'Visa Platinum',    12000.00,   800.00, 0.1899, '2021-11-01', '2026-11-01', 3400),
(11, '5500000000000002', 'Mastercard Black', 35000.00,  9200.00, 0.1599, '2020-01-01', '2025-01-01', 28000),
(14, '4111111111111006', 'Visa Signature',   20000.00,  4100.00, 0.1699, '2021-04-01', '2026-04-01', 8700),
(17, '4111111111111007', 'Visa Platinum',    15000.00,   300.00, 0.1799, '2022-08-01', '2027-08-01', 5200),
(19, '4111111111111008', 'Visa Gold',        10000.00,  2800.00, 0.1999, '2023-01-01', '2028-01-01', 2900),
(21, '5500000000000003', 'Mastercard World', 30000.00,  6700.00, 0.1599, '2020-05-01', '2025-05-01', 18500),
(27, '4111111111111009', 'Visa Gold',        12000.00,   450.00, 0.1899, '2022-02-01', '2027-02-01', 6100),
(37, '5500000000000004', 'Mastercard Black', 75000.00, 12500.00, 0.1399, '2019-06-01', '2024-06-01', 95000),
(46, '4111111111111010', 'Visa Signature',   25000.00,  1100.00, 0.1599, '2021-03-01', '2026-03-01', 14200);

-- -----------------------------------------------------------------------------
-- CREDIT CARD TRANSACTIONS  (80 transactions)
-- -----------------------------------------------------------------------------
INSERT INTO credit_card_transactions (card_id, amount, transaction_date, merchant_name, merchant_category, city, state, is_international) VALUES
-- Card 1 (Liam)
(1,  45.50,  '2025-01-03 12:00:00-05', 'Amazon',              'online_retail',   'Seattle',     'WA', FALSE),
(1, 120.00,  '2025-01-10 19:30:00-05', 'Nobu NYC',            'restaurant',      'New York',    'NY', FALSE),
(1, 299.99,  '2025-01-22 14:00:00-05', 'Best Buy',            'electronics',     'New York',    'NY', FALSE),
(1,  55.00,  '2025-02-05 08:00:00-05', 'Delta Airlines',      'travel',          'New York',    'NY', FALSE),
(1, 850.00,  '2025-02-20 10:00:00-05', 'Hotel Le Marais',     'travel',          'Paris',       NULL, TRUE),
(1,  30.00,  '2025-03-01 20:00:00-05', 'Spotify',             'entertainment',   'Stockholm',   NULL, TRUE),
(1, 200.00,  '2025-03-15 11:00:00-05', 'Saks Fifth Avenue',   'retail',          'New York',    'NY', FALSE),
(1,  75.25,  '2025-04-08 13:00:00-05', 'Whole Foods',         'grocery',         'New York',    'NY', FALSE),
(1, 180.00,  '2025-05-02 21:00:00-05', 'Broadway Tickets',    'entertainment',   'New York',    'NY', FALSE),
-- Card 2 (Emma)
(2, 2500.00, '2025-01-18 15:00:00-05', 'Bergdorf Goodman',    'retail',          'New York',    'NY', FALSE),
(2,  320.00, '2025-01-25 18:30:00-05', 'Nobu NYC',            'restaurant',      'New York',    'NY', FALSE),
(2, 1800.00, '2025-02-10 10:00:00-05', 'Lufthansa Airlines',  'travel',          'Frankfurt',   NULL, TRUE),
(2,  550.00, '2025-02-12 14:00:00-05', 'Hotel Adlon',         'travel',          'Berlin',      NULL, TRUE),
(2,  420.00, '2025-03-05 20:00:00-05', 'Michelin Restaurant', 'restaurant',      'Paris',       NULL, TRUE),
(2,  180.00, '2025-03-20 12:00:00-05', 'Apple Store',         'electronics',     'New York',    'NY', FALSE),
(2,   95.00, '2025-04-01 09:00:00-05', 'SoulCycle',           'fitness',         'New York',    'NY', FALSE),
(2,  340.00, '2025-04-15 16:00:00-05', 'Net-a-Porter',        'retail',          'New York',    'NY', FALSE),
(2,  220.00, '2025-05-10 19:00:00-05', 'Le Bernardin',        'restaurant',      'New York',    'NY', FALSE),
-- Card 4 (Ava - HNW)
(4, 5000.00, '2025-01-05 14:00:00-05', 'Tiffany & Co',        'luxury_retail',   'New York',    'NY', FALSE),
(4, 3200.00, '2025-01-20 18:00:00-05', 'Per Se',              'restaurant',      'New York',    'NY', FALSE),
(4, 8500.00, '2025-02-01 10:00:00-05', 'Four Seasons Paris',  'travel',          'Paris',       NULL, TRUE),
(4, 2200.00, '2025-02-15 16:00:00-05', 'Louis Vuitton',       'luxury_retail',   'Paris',       NULL, TRUE),
(4, 1500.00, '2025-03-10 20:00:00-05', 'Daniel Restaurant',   'restaurant',      'New York',    'NY', FALSE),
(4,  780.00, '2025-03-25 11:00:00-05', 'Net Jets deposit',    'travel',          'New York',    'NY', FALSE),
(4, 4200.00, '2025-04-08 15:00:00-05', 'Christie''s Auction', 'luxury_retail',   'New York',    'NY', FALSE),
(4, 2800.00, '2025-04-20 19:00:00-05', 'Gordon Ramsay Bar',   'restaurant',      'Las Vegas',   'NV', FALSE),
-- Card 5 (James Davis)
(5,  189.00, '2025-01-08 18:30:00-06', 'Cheesecake Factory',  'restaurant',      'Chicago',     'IL', FALSE),
(5,   45.00, '2025-01-15 09:00:00-06', 'Shell',               'gas_station',     'Chicago',     'IL', FALSE),
(5,  320.00, '2025-01-28 12:00:00-06', 'Target',              'retail',          'Chicago',     'IL', FALSE),
(5,  210.00, '2025-02-10 20:00:00-06', 'Gibsons Restaurant',  'restaurant',      'Chicago',     'IL', FALSE),
(5,   85.00, '2025-03-01 08:00:00-06', 'BP Gas',              'gas_station',     'Chicago',     'IL', FALSE),
(5,  450.00, '2025-03-15 14:00:00-06', 'Macy''s',             'retail',          'Chicago',     'IL', FALSE),
-- Card 7 (Ava - Mastercard Black)
(7, 3500.00, '2025-01-10 16:00:00-05', 'Neiman Marcus',       'luxury_retail',   'New York',    'NY', FALSE),
(7, 1200.00, '2025-01-22 20:00:00-05', 'Nobu NYC',            'restaurant',      'New York',    'NY', FALSE),
(7, 5800.00, '2025-02-03 11:00:00-05', 'Mandarin Oriental',   'travel',          'Hong Kong',   NULL, TRUE),
(7, 1900.00, '2025-02-18 14:00:00-05', 'Rolex Boutique',      'luxury_retail',   'Hong Kong',   NULL, TRUE),
(7,  650.00, '2025-03-05 21:00:00-05', 'Masa Restaurant',     'restaurant',      'New York',    'NY', FALSE),
(7, 2100.00, '2025-04-01 10:00:00-05', 'Gucci',               'luxury_retail',   'New York',    'NY', FALSE),
-- Potentially fraudulent pattern (card 5 - James Davis, unusual activity)
(5,  999.00, '2025-03-22 02:10:00-06', 'Online Electronics',  'electronics',     'Miami',       'FL', FALSE),
(5,  999.00, '2025-03-22 02:15:00-06', 'Online Electronics',  'electronics',     'Miami',       'FL', FALSE),
(5, 1500.00, '2025-03-22 02:45:00-06', 'Crypto Exchange',     'unknown',         'London',      NULL, TRUE),
-- More regular transactions
(8,  250.00, '2025-01-10 15:00:00-08', 'REI',                 'retail',          'Seattle',     'WA', FALSE),
(8,  380.00, '2025-01-20 18:00:00-08', 'Pike Place Chowder',  'restaurant',      'Seattle',     'WA', FALSE),
(8,  120.00, '2025-02-05 11:00:00-08', 'Costco',              'grocery',         'Seattle',     'WA', FALSE),
(8,  680.00, '2025-02-14 20:00:00-08', 'Anthony''s Pier 66',  'restaurant',      'Seattle',     'WA', FALSE),
(8,  420.00, '2025-03-10 13:00:00-08', 'Nordstrom',           'retail',          'Seattle',     'WA', FALSE),
(10, 890.00, '2025-01-15 12:00:00-05', 'Amazon',              'online_retail',   'Seattle',     'WA', FALSE),
(10, 450.00, '2025-02-08 19:00:00-05', 'Capital Grille',      'restaurant',      'Washington',  'DC', FALSE),
(10, 220.00, '2025-02-22 14:00:00-05', 'Giant Food',          'grocery',         'Washington',  'DC', FALSE),
(10, 650.00, '2025-03-18 11:00:00-05', 'Brooks Brothers',     'retail',          'Washington',  'DC', FALSE),
(11, 1800.00,'2025-01-12 10:00:00-10', 'Whole Foods',         'grocery',         'Miami',       'FL', FALSE),
(11, 4200.00,'2025-01-28 18:00:00-10', 'Zuma Miami',          'restaurant',      'Miami',       'FL', FALSE),
(11, 2900.00,'2025-02-20 16:00:00-10', 'Net-a-Porter',        'retail',          'Miami',       'FL', FALSE),
(12, 320.00, '2025-01-05 14:00:00-08', 'Starbucks Corp',      'cafe',            'San Jose',    'CA', FALSE),
(12,  89.00, '2025-01-18 10:00:00-08', 'Safeway',             'grocery',         'San Jose',    'CA', FALSE),
(12, 550.00, '2025-02-12 17:00:00-08', 'Best Buy',            'electronics',     'San Jose',    'CA', FALSE),
(13, 145.00, '2025-01-09 13:00:00-05', 'Whole Foods',         'grocery',         'Washington',  'DC', FALSE),
(13, 380.00, '2025-01-25 20:00:00-05', 'Jose Andres TBC',     'restaurant',      'Washington',  'DC', FALSE),
(13, 800.00, '2025-02-15 11:00:00-05', 'Brooks Brothers',     'retail',          'Washington',  'DC', FALSE),
(14, 280.00, '2025-01-14 10:00:00-10', 'Miami Seaquarium',    'entertainment',   'Miami',       'FL', FALSE),
(14, 950.00, '2025-02-03 18:00:00-10', 'Nobu Miami',          'restaurant',      'Miami',       'FL', FALSE),
(14, 1200.00,'2025-03-08 15:00:00-10', 'Bloomingdale''s',     'retail',          'Miami',       'FL', FALSE);

-- -----------------------------------------------------------------------------
-- LOANS  (20 loans across various customers)
-- -----------------------------------------------------------------------------
INSERT INTO loans (customer_id, branch_id, loan_type, principal, outstanding_balance,
    interest_rate, origination_date, maturity_date, monthly_payment, status, collateral_type) VALUES
(1,  1,  'mortgage',      380000.00,  345200.00, 0.0625, '2018-06-01', '2048-06-01', 2340.00, 'active',    'residential_property'),
(2,  1,  'mortgage',      750000.00,  720800.00, 0.0595, '2020-03-01', '2050-03-01', 4520.00, 'active',    'residential_property'),
(5,  2,  'auto',           45000.00,   22400.00, 0.0499, '2022-08-01', '2027-08-01',  848.00, 'active',    'vehicle'),
(6,  2,  'mortgage',     1200000.00, 1145000.00, 0.0550, '2019-01-01', '2049-01-01', 6810.00, 'active',    'residential_property'),
(7,  4,  'auto',           28000.00,   15600.00, 0.0525, '2021-05-01', '2026-05-01',  532.00, 'active',    'vehicle'),
(8,  5,  'personal',       10000.00,    6800.00, 0.1499, '2023-01-01', '2026-01-01',  347.00, 'active',    NULL),
(9,  4,  'auto',           35000.00,    8200.00, 0.0479, '2020-03-01', '2025-03-01',  660.00, 'paid_off',  'vehicle'),
(11, 6,  'mortgage',      890000.00,  854000.00, 0.0575, '2018-09-01', '2048-09-01', 5190.00, 'active',    'residential_property'),
(11, 6,  'home_equity',   150000.00,   82000.00, 0.0750, '2021-04-01', '2031-04-01', 1780.00, 'active',    'residential_property'),
(12, 6,  'personal',        8000.00,    4100.00, 0.1599, '2022-06-01', '2025-06-01',  281.00, 'delinquent',NULL),
(14, 7,  'mortgage',      620000.00,  582000.00, 0.0610, '2019-06-01', '2049-06-01', 3780.00, 'active',    'residential_property'),
(15, 8,  'auto',           32000.00,   18900.00, 0.0510, '2021-11-01', '2026-11-01',  607.00, 'active',    'vehicle'),
(17, 8,  'mortgage',      440000.00,  395000.00, 0.0640, '2017-04-01', '2047-04-01', 2754.00, 'active',    'residential_property'),
(18, 9,  'student',        45000.00,   38000.00, 0.0550, '2020-08-01', '2030-08-01',  487.00, 'active',    NULL),
(19, 9,  'auto',           42000.00,   28000.00, 0.0495, '2022-01-01', '2027-01-01',  793.00, 'active',    'vehicle'),
(21, 10, 'mortgage',      580000.00,  550000.00, 0.0615, '2020-07-01', '2050-07-01', 3540.00, 'active',    'residential_property'),
(22, 2,  'auto',           26000.00,   11000.00, 0.0520, '2021-03-01', '2026-03-01',  493.00, 'active',    'vehicle'),
(23, 1,  'personal',        5000.00,    2800.00, 0.1299, '2023-04-01', '2025-04-01',  239.00, 'active',    NULL),
(37, 1,  'mortgage',     1800000.00, 1680000.00, 0.0525, '2018-01-01', '2048-01-01', 9930.00, 'active',    'residential_property'),
(46, 9,  'mortgage',      520000.00,  462000.00, 0.0600, '2016-08-01', '2046-08-01', 3120.00, 'active',    'residential_property');

-- -----------------------------------------------------------------------------
-- LOAN PAYMENTS  (sample payment history for first 5 loans)
-- -----------------------------------------------------------------------------
INSERT INTO loan_payments (loan_id, payment_date, amount_paid, principal_portion, interest_portion, late_fee, days_late) VALUES
-- Loan 1 (Liam - mortgage)
(1, '2025-01-01', 2340.00, 354.84, 1985.16, 0.00, 0),
(1, '2025-02-01', 2340.00, 356.70, 1983.30, 0.00, 0),
(1, '2025-03-01', 2340.00, 358.57, 1981.43, 0.00, 0),
(1, '2025-04-01', 2340.00, 360.46, 1979.54, 0.00, 0),
(1, '2025-05-01', 2340.00, 362.36, 1977.64, 0.00, 0),
(1, '2025-06-01', 2340.00, 364.27, 1975.73, 0.00, 0),
-- Loan 5 (James - auto)
(5, '2025-01-01',  532.00, 463.22,  68.78, 0.00, 0),
(5, '2025-02-01',  532.00, 465.25,  66.75, 0.00, 0),
(5, '2025-03-01',  532.00, 467.30,  64.70, 0.00, 0),
(5, '2025-04-01',  532.00, 469.36,  62.64, 0.00, 0),
-- Loan 6 (Sophia - personal, delinquent)
(6, '2025-01-01',  347.00, 221.75, 125.25, 0.00,  0),
(6, '2025-02-01',  347.00, 225.06, 121.94, 0.00,  0),
(6, '2025-04-08',  347.00, 228.40, 118.60, 35.00, 37),
-- Loan 8 (Mason - mortgage)
(8, '2025-01-01', 5190.00, 924.50, 4265.50, 0.00, 0),
(8, '2025-02-01', 5190.00, 928.93, 4261.07, 0.00, 0),
(8, '2025-03-01', 5190.00, 933.39, 4256.61, 0.00, 0),
(8, '2025-04-01', 5190.00, 937.87, 4252.13, 0.00, 0),
(8, '2025-05-01', 5190.00, 942.38, 4247.62, 0.00, 0),
-- Loan 12 (Aiden - auto)
(12,'2025-01-01',  607.00, 446.60,  160.40, 0.00, 0),
(12,'2025-02-01',  607.00, 448.51,  158.49, 0.00, 0),
(12,'2025-03-01',  607.00, 450.43,  156.57, 0.00, 0),
(12,'2025-04-01',  607.00, 452.36,  154.64, 0.00, 0),
(12,'2025-05-01',  607.00, 454.30,  152.70, 0.00, 0),
(12,'2025-06-01',  607.00, 456.25,  150.75, 0.00, 0);

-- -----------------------------------------------------------------------------
-- FRAUD ALERTS
-- -----------------------------------------------------------------------------
INSERT INTO fraud_alerts (transaction_id, cc_transaction_id, customer_id, alert_date, alert_reason, risk_score, status, resolved_date, investigator_id) VALUES
-- Bank transaction fraud: Sophia unusual ATM at 2am
(84, NULL, 8, '2025-03-01 02:30:00-06', 'Large ATM withdrawal at unusual hour (2:15am)',           88.5, 'confirmed',    '2025-03-05 10:00:00-06', 18),
(85, NULL, 8, '2025-03-01 03:00:00-06', 'Negative balance after rapid sequential withdrawals',     92.0, 'confirmed',    '2025-03-05 10:00:00-06', 18),
-- Credit card fraud: James rapid duplicate charges
(NULL, 42, 7, '2025-03-22 02:20:00-06', 'Duplicate amount ($999) charged within 5 minutes',       85.0, 'investigating',NULL,                    18),
(NULL, 43, 7, '2025-03-22 02:20:00-06', 'Rapid sequential transactions different merchants 2am',  90.0, 'investigating',NULL,                    18),
(NULL, 44, 7, '2025-03-22 03:00:00-06', 'International crypto exchange transaction at 2:45am',    95.0, 'open',         NULL,                    NULL),
-- Low risk velocity check
(NULL, 18, 4, '2025-02-10 11:00:00-05', 'International transaction velocity check: 2 countries',  45.0, 'dismissed',   '2025-02-10 15:00:00-05', 18);
