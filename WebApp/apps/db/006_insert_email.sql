CREATE OR REPLACE FUNCTION fn_email_insert(
    p_user_id INTEGER,
    p_account_id INTEGER,
    p_provider_email_id TEXT,
    p_thread_id TEXT,
    p_subject TEXT,
    p_sender TEXT,
    p_recipients TEXT[],
    p_snippet TEXT,
    p_received_at TIMESTAMP,
    p_cached_body TEXT
)
RETURNS TABLE (
    status INTEGER,
    email_id INTEGER,
    message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_email_id INTEGER;
BEGIN

    INSERT INTO emails (
        user_id,
        account_id,
        provider_email_id,
        thread_id,
        subject,
        sender,
        recipients,
        snippet,
        received_at,
        cached_body
    )
    VALUES (
        p_user_id,
        p_account_id,
        p_provider_email_id,
        p_thread_id,
        p_subject,
        p_sender,
        p_recipients,
        p_snippet,
        p_received_at,
        p_cached_body
    )
    RETURNING id
    INTO v_email_id;

    RETURN QUERY
    SELECT
        1,
        v_email_id,
        'Email inserted successfully';

EXCEPTION

    WHEN unique_violation THEN
        RETURN QUERY
        SELECT
            0,
            NULL::INTEGER,
            'Email already exists';

    WHEN foreign_key_violation THEN
        RETURN QUERY
        SELECT
            0,
            NULL::INTEGER,
            'Invalid user or account';

    WHEN check_violation THEN
        RETURN QUERY
        SELECT
            0,
            NULL::INTEGER,
            'Validation failed';

END;
$$;

/**
SELECT *
FROM fn_email_insert(
    1,
    1,
    'gmail_123456'::TEXT,
    'thread_123'::TEXT,
    'Project Update'::TEXT,
    'john@example.com'::TEXT,
    ARRAY['sipho@example.com']::TEXT[],
    'Quick update on the project'::TEXT,
    NOW()::TIMESTAMP,
    'Full email body here'::TEXT
);
*/
