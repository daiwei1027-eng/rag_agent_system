# SEC test review — frozen

Frozen on 2026-10-22 following explicit user confirmation. See review_record.json. Historical review guidance in the JSON records is retained for provenance.

Reserved test content: use for annotation review and final frozen evaluation, not prompt/retrieval tuning.

## sec_test_001 | table_numeric

According to Microsoft's FY2026 MD&A, what was FY2026 sales and marketing expense in USD millions and its share of revenue?

Reference answer: USD 26,710 million, or 8% of revenue.

Fact group: msft_sales_marketing_2026; status: reviewed

Source: msft-2026-10k_item_7_b0133_c000 (answer)

> (In millions, except percentages) | 2026 |  | 2025 |  | Percentage Change | 
> Sales and marketing | $ | 26,710 | $ | 25,654 |  | 4%
> As a percent of revenue |  | 8% |  | 9% |  | (1)ppt

Decision: approved as part of the user-confirmed batch; no content revision during freeze.

## sec_test_002 | definition

In Microsoft's FY2025 MD&A metrics definitions, what does Microsoft 365 Commercial seat growth measure, and what qualifies as a seat?

Reference answer: The number of Microsoft 365 Commercial seats at period end; seats are paid users covered by a Microsoft 365 Commercial subscription.

Fact group: msft_commercial_seat_definition; status: reviewed

Source: msft-2025-10k_item_7_b0049_c000 (answer)

> Microsoft 365 Commercial cloud revenue growth | Revenue from Microsoft 365 Commercial subscriptions, comprising Microsoft 365 Commercial, Enterprise Mobility + Security, the cloud portion of Windows Commercial, the per-user portion of Power BI, Exchange, SharePoint, Microsoft Teams, Microsoft 365 Security and Compliance, and Microsoft 365 Copilot
> Microsoft 365 Commercial seat growth | The number of Microsoft 365 Commercial seats at end of period where seats are paid users covered by a Microsoft 365 Commercial subscription
> Microsoft 365 Consumer cloud revenue growth | Revenue from Microsoft 365 Consumer subscriptions and other consumer services
> Microsoft 365 Consumer subscribers | The number of Microsoft 365 Consumer subscribers at end of period
> LinkedIn revenue growth | Revenue from LinkedIn, including Talent Solutions, Marketing Solutions, Premium Subscriptions, and Sales Solutions
> Dynamics 365 revenue growth | Revenue from Dynamics 365, including a set of intelligent, cloud-based applications across ERP, CRM, Power Apps, and Power Automate

Decision: approved as part of the user-confirmed batch; no content revision during freeze.

## sec_test_003 | business_fact

Who is listed as NVIDIA's Executive Vice President and Chief Financial Officer in its FY2026 Business-section executive-officer table?

Reference answer: Colette M. Kress.

Fact group: nvda_finance_leadership_2026; status: reviewed

Source: nvda-2026-10k_item_1_b0134_c000 (answer)

> Name | Age | Position
> Jen-Hsun Huang | 63 | President and Chief Executive Officer
> Colette M. Kress | 58 | Executive Vice President and Chief Financial Officer
> Ajay K. Puri | 71 | Executive Vice President, Worldwide Field Operations
> Debora Shoquist | 71 | Executive Vice President, Operations
> Timothy S. Teter | 59 | Executive Vice President and General Counsel

Decision: approved as part of the user-confirmed batch; no content revision during freeze.

## sec_test_004 | table_numeric

In NVIDIA's FY2025 MD&A customer-concentration table, what percentage of revenue is attributed to Direct Customer A for the year ended January 26, 2025?

Reference answer: 12%.

Fact group: nvda_anonymous_customer_a_2025; status: reviewed

Source: nvda-2025-10k_item_7_b0087_c000 (answer)

>  | Year Ended |  |  | 
>  | Jan 26, 2025 |  | Jan 28, 2024 | 
> Direct Customer A | 12 | % | * | 
> Direct Customer B | 11 | % | 13 | %
> Direct Customer C | 11 | % | * | 

Decision: approved as part of the user-confirmed batch; no content revision during freeze.

## sec_test_005 | calculation

Using Alphabet's FY2025 MD&A tax table, what were the effective tax rates in 2024 and 2025, and by how many percentage points did the rate change?

Reference answer: 16.4% in 2024 and 16.8% in 2025; an increase of 0.4 percentage points.

Fact group: goog_effective_tax_2025; status: reviewed

Source: goog-2025-10k_item_7_b0212_c000 (answer)

>  | Year Ended December 31, |  |  |  |  | 
>  | 2024 |  |  | 2025 |  | 
> Income before provision for income taxes | $ | 119,815 |  | $ | 158,826 | 
> Provision for income taxes | $ | 19,697 |  | $ | 26,656 | 
> Effective tax rate | 16.4 |  | % | 16.8 |  | %

Calculation: [{"operation": "subtract", "operands": [16.8, 16.4], "expected_result": 0.4, "unit": "percentage points"}]

Decision: approved as part of the user-confirmed batch; no content revision during freeze.

## sec_test_006 | multi_evidence

According to Alphabet's FY2024 MD&A repurchase table, how many Class C shares were repurchased and retired in 2024, and for what amount? State both units.

Reference answer: 306 million Class C shares for USD 50,192 million.

Fact group: goog_class_c_repurchases_2024; status: reviewed

Source: goog-2024-10k_item_7_b0286_c000 (values)

>  | Year Ended December 31, 2023 |  |  | Year Ended December 31, 2024 |  | 
>  | Shares | Amount |  | Shares | Amount | 
> Class A share repurchases | 78 | $ | 9,316 | 73 | $ | 11,855
> Class C share repurchases | 450 | 52,868 |  | 306 | 50,192 | 
> Total share repurchases(1) | 528 | $ | 62,184 | 379 | $ | 62,047

Source: goog-2024-10k_item_7_b0285_c000 (units)

> The following table presents Class A and Class C shares repurchased and subsequently retired (in millions):

Decision: approved as part of the user-confirmed batch; no content revision during freeze.

## sec_test_007 | business_fact

As of June 30, 2026, how many full-time employees did Microsoft report in its FY2026 Business section, and how were they split between the U.S. and international locations?

Reference answer: Approximately 223,000 full-time employees: 121,000 in the U.S. and 102,000 internationally.

Fact group: msft_headcount_2026; status: reviewed

Source: msft-2026-10k_item_1_b0126_c000 (answer)

> As of June 30, 2026, we employed approximately 223,000 people on a full-time basis, 121,000 in the U.S. and 102,000 internationally. Of the total employees, 89,000 were in operations, including product support and consulting services, datacenter operations, and manufacturing and distribution; 77,000 were in product research and development; 43,000 were in sales and marketing; and 14,000 were in general and administration. Certain employees are subject to collective bargaining agreements.

Decision: approved as part of the user-confirmed batch; no content revision during freeze.

## sec_test_008 | risk_paraphrase

What consequences for user data and access to services does Alphabet's FY2025 Risk Factors section associate with security breaches and attacks?

Reference answer: Improper disclosure and use of user data, and interference with users and customers being able to use products and services, harming the business and reputation.

Fact group: goog_user_data_security_risk_2025; status: reviewed

Source: goog-2025-10k_item_1a_b0082_c000 (answer)

> Data privacy and security concerns relating to our technology and our practices could harm our reputation, cause us to incur significant liability, and deter current and potential users or customers from using our products and services. Computer viruses, software bugs or defects, security breaches, and attacks on our systems could result in the improper disclosure and use of user data and interference with our users' and customers' ability to use our products and services, harming our business and reputation.

Decision: approved as part of the user-confirmed batch; no content revision during freeze.

## sec_test_009 | unanswerable

What is the legal company name of Direct Customer A in NVIDIA's FY2025 MD&A customer-concentration table, according to the supplied FY2025 excerpts?

Reference answer: The requested exact information cannot be determined from the supplied Business, Risk Factors and MD&A excerpts. Do not substitute an aggregate, an estimate or outside knowledge.

Fact group: nvda_anonymous_customer_a_2025; status: reviewed

Scope: nvda-2025-10k, 544 chunks from Item 1/1A/7.

Draft rationale: An anonymized customer label and its percentage do not establish the customer legal identity; do not infer a name from outside knowledge.

Inspect the scoped chunks and nearby candidate contexts in the absence evidence JSON; keyword matches are not proof of absence.

Decision: approved as part of the user-confirmed batch; no content revision during freeze.

## sec_test_010 | unanswerable

What was revenue from the Gemini app alone in USD during 2025, excluding other Google subscription and cloud offerings, according to Alphabet's supplied FY2025 excerpts?

Reference answer: The requested exact information cannot be determined from the supplied Business, Risk Factors and MD&A excerpts. Do not substitute an aggregate, an estimate or outside knowledge.

Fact group: goog_gemini_app_revenue_2025; status: reviewed

Scope: goog-2025-10k, 513 chunks from Item 1/1A/7.

Draft rationale: Product and subscription discussion and aggregate revenue do not establish a full-year Gemini-app-only revenue figure.

Inspect the scoped chunks and nearby candidate contexts in the absence evidence JSON; keyword matches are not proof of absence.

Decision: approved as part of the user-confirmed batch; no content revision during freeze.

