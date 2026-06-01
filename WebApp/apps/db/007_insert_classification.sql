CREATE OR REPLACE FUNCTION fn_classification_insert(
    p_email_id INTEGER,
    p_label TEXT,
    p_confidence NUMERIC(5,4),
    p_model_version TEXT,
    p_source TEXT
)
RETURNS TABLE (
    status INTEGER,
    classification_id INTEGER,
    message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_classification_id INTEGER;
BEGIN

    INSERT INTO classifications (
        email_id,
        label,
        confidence,
        model_version,
        source
    )
    VALUES (
        p_email_id,
        LOWER(p_label),
        p_confidence,
        p_model_version,
        p_source
    )
    RETURNING id
    INTO v_classification_id;

    RETURN QUERY
    SELECT
        1,
        v_classification_id,
        'Classification created successfully';

EXCEPTION

    WHEN foreign_key_violation THEN
        RETURN QUERY
        SELECT
            0,
            NULL::INTEGER,
            'Email does not exist';

    WHEN check_violation THEN
        RETURN QUERY
        SELECT
            0,
            NULL::INTEGER,
            'Invalid classification label';

END;
$$;
/*Test insert function 
SELECT *
FROM fn_classification_insert(
    1,
    'spam',
    0.9821,
    'v1.0',
    'model'
);*/