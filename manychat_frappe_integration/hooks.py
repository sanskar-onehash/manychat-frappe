app_name = "manychat_frappe_integration"
app_title = "Manychat Frappe Integration"
app_publisher = "sukhman@onehash.ai"
app_description = "Manychat and Frappe integration"
app_email = "sukhman@onehash.ai"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "manychat_frappe_integration",
# 		"logo": "/assets/manychat_frappe_integration/logo.png",
# 		"title": "Manychat Frappe Integration",
# 		"route": "/manychat_frappe_integration",
# 		"has_permission": "manychat_frappe_integration.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/manychat_frappe_integration/css/manychat_frappe_integration.css"
# app_include_js = "/assets/frappe_meta_integration/js/toolbar.js"
app_include_js = "/assets/manychat_frappe_integration/js/toolbar.js"
# app_include_js = "/assets/manychat_frappe_integration/js/list_view.js"
# app_include_js = "/assets/manychat_frappe_integration/js/subscriber.js"

# include js, css files in header of web template
# web_include_css = "/assets/manychat_frappe_integration/css/manychat_frappe_integration.css"
# web_include_js = "/assets/manychat_frappe_integration/js/manychat_frappe_integration.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "manychat_frappe_integration/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}
page_js = {"page" : "public/js/subscriber.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "manychat_frappe_integration/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "manychat_frappe_integration.utils.jinja_methods",
# 	"filters": "manychat_frappe_integration.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "manychat_frappe_integration.install.before_install"
# after_install = "manychat_frappe_integration.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "manychat_frappe_integration.uninstall.before_uninstall"
# after_uninstall = "manychat_frappe_integration.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "manychat_frappe_integration.utils.before_app_install"
# after_app_install = "manychat_frappe_integration.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "manychat_frappe_integration.utils.before_app_uninstall"
# after_app_uninstall = "manychat_frappe_integration.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "manychat_frappe_integration.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

override_doctype_class = {
	"Notification": "manychat_frappe_integration.manychat_frappe_integration.overrides.notification.SendNotification"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"manychat_frappe_integration.tasks.all"
# 	],
# 	"daily": [
# 		"manychat_frappe_integration.tasks.daily"
# 	],
# 	"hourly": [
# 		"manychat_frappe_integration.tasks.hourly"
# 	],
# 	"weekly": [
# 		"manychat_frappe_integration.tasks.weekly"
# 	],
# 	"monthly": [
# 		"manychat_frappe_integration.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "manychat_frappe_integration.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "manychat_frappe_integration.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "manychat_frappe_integration.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["manychat_frappe_integration.utils.before_request"]
# after_request = ["manychat_frappe_integration.utils.after_request"]

# Job Events
# ----------
# before_job = ["manychat_frappe_integration.utils.before_job"]
# after_job = ["manychat_frappe_integration.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"manychat_frappe_integration.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

