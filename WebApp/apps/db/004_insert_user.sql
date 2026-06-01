CREATE OR REPLACE FUNCTION fn_user_insert(
    p_email TEXT,
    p_name TEXT
)
RETURNS TABLE (
    status INTEGER,
    user_id INTEGER,
    message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id INTEGER;
BEGIN

    INSERT INTO users (
        email,
        name
    )
    VALUES (
        p_email,
        p_name
    )
    RETURNING id
    INTO v_user_id;

    RETURN QUERY
    SELECT
        1,
        v_user_id,
        'User created successfully';

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
            'Related record does not exist';

    WHEN check_violation THEN
        RETURN QUERY
        SELECT
            0,
            NULL::INTEGER,
            'Validation failed';
END;
$$;
/*
Test insert function 
SELECT *
FROM fn_user_insert(
    'sipho@example.com',
    'Sipho Ntobela'
);*/