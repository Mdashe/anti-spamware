SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'email_classifier';

DROP DATABASE IF EXISTS email_classifier;