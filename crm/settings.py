INSTALLED_APPS = [
    # other apps
    'django_crontab',
    'crm',  # your app
]

CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 8 * * *', 'crm.cron.send_order_reminders'),
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]
