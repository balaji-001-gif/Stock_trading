# BIZAXL - Investment & Wealth Platform
# App Hooks — Central configuration file

from . import __version__ as app_version

app_name = "bizaxl"
app_title = "BIZAXL"
app_publisher = "bizaxl Optimisations LLP"
app_description = "Investment & Wealth Platform — 12 Investment Verticals"
app_email = "dev@bizaxl.com"
app_icon = "octicon octicon-graph"
app_color = "green"
app_logo_url = "/assets/bizaxl/images/logo.svg"
app_url = "https://bizaxl.com"
app_version = app_version
app_license = "GNU General Public License v3"

# ----------------------------------------------------------------------------
# Modules
# ----------------------------------------------------------------------------
# List of modules in this app. Each module groups related DocTypes together.
app_modules = [
    "Investment Core",
    "Mutual Funds",
    "Portfolio Management Services",
    "Alternative Investment Funds",
    "Private Equity",
    "Venture Capital",
    "Bonds Fixed Deposits",
    "Real Estate Funds",
    "Stock Broking",
    "Family Office",
    "Pension Funds",
    "Advisor Portal",
    "Compliance Regulatory",
    "Reports Analytics",
]

# ----------------------------------------------------------------------------
# DocType Class Overrides
# ----------------------------------------------------------------------------
# Override standard Frappe DocType classes with custom controllers
# doc_type_class = {
#     "Fund Master": "bizaxl.bizaxl.doctype.fund_master.fund_master.FundMaster",
# }

# ----------------------------------------------------------------------------
# Before/After Migrate
# ----------------------------------------------------------------------------
# before_migrate = "bizaxl.setup.install.before_migrate"
# after_migrate = "bizaxl.setup.install.after_migrate"

# ----------------------------------------------------------------------------
# Before/After Install
# ----------------------------------------------------------------------------
# before_install = "bizaxl.setup.install.before_install"
after_install = "bizaxl.setup.after_install"

# ----------------------------------------------------------------------------
# Desk
# ----------------------------------------------------------------------------
# Custom setup for the desk
# setup_requirements = "bizaxl.setup.setup_requirements"

# ----------------------------------------------------------------------------
# Website
# ----------------------------------------------------------------------------
# website_route_rules = []
# website_context = {}

# ----------------------------------------------------------------------------
# Calendar
# ----------------------------------------------------------------------------
# Calendar DocTypes that appear in the calendar view
# calendar_doctypes = []

# ----------------------------------------------------------------------------
# User Data Protection
# ----------------------------------------------------------------------------
# user_data_fields = [
#     {
#         "doctype": "{doctype_1}",
#         "filter_by": "user",
#         "redact_fields": [],
#         "partial": 1,
#     },
# ]

# ----------------------------------------------------------------------------
# Authentication & API
# ----------------------------------------------------------------------------
# auth_hooks = []
# api_allow_methods = []

# ----------------------------------------------------------------------------
# Translation
# ----------------------------------------------------------------------------
# translations_pattern = "*.csv"
# translations_directory = "bizaxl"

# ----------------------------------------------------------------------------
# Document Events
# ----------------------------------------------------------------------------
# Hook into DocType events (validate, on_update, on_submit, etc.)
# doc_events = {
#     "Fund Master": {
#         "validate": "bizaxl.bizaxl.doctype.fund_master.fund_master.validate",
#         "on_update": "bizaxl.bizaxl.doctype.fund_master.fund_master.on_update",
#     }
# }

# ----------------------------------------------------------------------------
# Scheduled Tasks
# ----------------------------------------------------------------------------
# scheduler_events = {
#     "daily": [
#         "bizaxl.bizaxl.doctype.nav_engine.tasks.daily_nav_calculation"
#     ],
#     "daily_long": [],
#     "weekly": [],
#     "monthly": [],
# }

# ----------------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------------
fixtures = [
    {
        "dt": "Workspace",
        "filters": [
            ["module", "in", [
                "Investment Core",
                "Mutual Funds",
                "Portfolio Management Services",
                "Alternative Investment Funds",
                "Private Equity",
                "Venture Capital",
                "Bonds Fixed Deposits",
                "Real Estate Funds",
                "Stock Broking",
                "Family Office",
                "Pension Funds",
                "Advisor Portal",
                "Compliance Regulatory",
                "Reports Analytics",
            ]]
        ]
    },
]

# ----------------------------------------------------------------------------
# Permissions
# ----------------------------------------------------------------------------
# permission_query_conditions = {
#     "Fund Master": "bizaxl.bizaxl.doctype.fund_master.fund_master.get_permission_query_conditions",
# }

# has_permission = {
#     "Fund Master": "bizaxl.bizaxl.doctype.fund_master.fund_master.has_permission",
# }

# ----------------------------------------------------------------------------
# Custom Fields
# ----------------------------------------------------------------------------
# custom_fields = {
#     "Sales Invoice": [
#         {
#             "fieldname": "bizaxl_investment_id",
#             "label": "BIZAXL Investment Reference",
#             "fieldtype": "Data",
#             "insert_after": "custom_1",
#         }
#     ]
# }

# ----------------------------------------------------------------------------
# Property Setters
# ----------------------------------------------------------------------------
# property_setters = []

# ----------------------------------------------------------------------------
# Print Formats
# ----------------------------------------------------------------------------
# print_format_template = {
#     "Capital Account Statement": "templates/print_format/capital_account_statement.html",
# }

# ----------------------------------------------------------------------------
# Notification
# ----------------------------------------------------------------------------
# notification_config = "bizaxl.bizaxl.notifications.get_notification_config"

# ----------------------------------------------------------------------------
# Jinja
# ----------------------------------------------------------------------------
# jinja = {}
