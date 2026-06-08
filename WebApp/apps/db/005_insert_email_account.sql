/*check as reference, the function 004_insert_user.sql*/
/*Also note for testing the function, you need to insert a user first and use the returned user_id for the email account insertion*/
/*CREATE OR REPLACE FUNCTION fn_email_account_insert(

Test insert function 
SELECT *
FROM fn_user_insert(
    'sipho@example.com',
    'Sipho Ntobela'
);*/

CREATE OR REPLACE FUNCTION fn_email_account_insert(
    p_user_id INTEGER,  /** should be the id of the user to whom the email account belongs */
    p_provider TEXT,   /** e.g., 'gmail', 'outlook' */
    p_provider_email TEXT,  /** the email address used with the provider, e.g., 'sipho@gmail.com' */
    p_access_token TEXT,    /** OAuth access token for API access */
    p_refresh_token TEXT,   /** OAuth refresh token for renewing access */
    p_expires_at TIMESTAMP     /* when the access token expires */
)
RETURNS TABLE (
    status INTEGER, /* 1 for success, 0 for failure */
    account_id INTEGER, /* the id of the newly created email account, or NULL on failure */
    message TEXT /* success or error message */
)
LANGUAGE  plpgsql  /* specify that this is a PL/pgSQL function */
AS $$   /* function body starts here */
DECLARE  /* declare any variables needed for the function */
    v_account_id INTEGER;  /* variable to hold the id of the newly inserted email account */
BEGIN  /* attempt to insert a new email account record into the email_accounts table */

    INSERT INTO email_accounts (
        user_id,  /* foreign key reference to users table */
        provider, /* email service provider name */
        provider_email, /* the email address associated with the provider */
        access_token,  /* token for API access */
        refresh_token, /* token for refreshing access */
        expires_at /* token expiration time */
    )
    VALUES (
        p_user_id,  /* the user_id passed as a parameter to the function */
        p_provider, /* the provider name passed as a parameter */
        p_provider_email, /* the provider email passed as a parameter */
        p_access_token, /* the access token passed as a parameter */
        p_refresh_token, /* the refresh token passed as a parameter */
        p_expires_at /* the expiration time passed as a parameter */
    )
    RETURNING id INTO v_account_id; /* after inserting, return the id of the new record into the variable v_account_id */

    RETURN QUERY /* if the insert is successful, return a success status, the new account id, and a success message */
    SELECT  /* return values */
        1,  /* status: 1 indicates success */
        v_account_id, /* the id of the newly created email account */
        'Email account linked successfully'; /* success message */

EXCEPTION /* handle exceptions that may occur during the insert operation */
    WHEN foreign_key_violation THEN /* if the user_id does not exist in the users table */
        RETURN QUERY SELECT 0, NULL::INTEGER, 'User does not exist'; /* return failure status and message */

    WHEN not_null_violation THEN /* if any required fields are missing */
        RETURN QUERY SELECT 0, NULL::INTEGER, 'Provider and email are required'; /* return failure status and message */

    WHEN unique_violation THEN /* if the provider_email already exists for the same provider */
        RETURN QUERY SELECT 0, NULL::INTEGER, 'Email account already linked'; /* return failure status and message */

    WHEN foreign_key_violation THEN /* if the user_id does not exist in the users table */
        RETURN QUERY SELECT 0, NULL::INTEGER, 'User does not exist'; /* return failure status and message */

    WHEN not_null_violation THEN
        RETURN QUERY SELECT 0, NULL::INTEGER, 'Provider and email are required'; /* return failure status and message */

    WHEN unique_violation THEN /* if the provider_email already exists for the same provider */
        RETURN QUERY SELECT 0, NULL::INTEGER, 'Email account already linked'; /* return failure status and message */

END; /* function body ends here *$
$$;


