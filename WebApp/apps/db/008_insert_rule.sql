CREATE OR REPLACE FUNCTION fn_rule_insert(
    p_user_id INTEGER,
    p_name TEXT,
    p_condition_type TEXT,
    p_condition_value TEXT,
    p_action TEXT,
    p_enabled BOOLEAN DEFAULT TRUE
)
RETURNS TABLE (
    status INTEGER,
    rule_id INTEGER,
    message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_rule_id INTEGER;
BEGIN

    INSERT INTO rules (
        user_id,
        name,
        condition_type,
        condition_value,
        action,
        enabled
    )
    VALUES (
        p_user_id,
        p_name,
        p_condition_type,
        p_condition_value,
        p_action,
        p_enabled
    )
    RETURNING id
    INTO v_rule_id;

    RETURN QUERY
    SELECT
        1,
        v_rule_id,
        'Rule created successfully';

EXCEPTION

    WHEN foreign_key_violation THEN
        RETURN QUERY
        SELECT
            0,
            NULL::INTEGER,
            'User does not exist';

    WHEN check_violation THEN
        RETURN QUERY
        SELECT
            0,
            NULL::INTEGER,
            'Invalid rule value';

END;
$$;
/*
SELECT *
FROM fn_rule_insert(
    1,
    'Spam Keywords',
    'subject_contains',
    'lottery',
    'mark_spam',
    TRUE
);*/