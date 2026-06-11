-- Portable table export: DROP + CREATE (from live schema) + INSERT rows.
-- Run this file once in pgAdmin on the source database, then call the function per table.
--
-- Example (pgAdmin Query Tool):
--   SELECT fn_export_table_script('users');
--   SELECT fn_export_table_script('emails', 'public');
--
-- Copy the result, paste into Query Tool on the target database, and execute.

CREATE OR REPLACE FUNCTION fn_export_table_script(
    p_table_name TEXT,
    p_schema_name TEXT DEFAULT 'public'
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_qualified TEXT;
    v_drop TEXT;
    v_create TEXT;
    v_inserts TEXT := '';
    v_sequences TEXT := '';
    v_row RECORD;
    v_col RECORD;
    v_cols TEXT;
    v_vals TEXT;
    v_val TEXT;
    v_seq_name TEXT;
    v_col_name TEXT;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = p_schema_name
          AND table_name = p_table_name
          AND table_type = 'BASE TABLE'
    ) THEN
        RAISE EXCEPTION 'Table %.% does not exist', p_schema_name, p_table_name;
    END IF;

    v_qualified := format('%I.%I', p_schema_name, p_table_name);

    -- DROP
    v_drop := format('DROP TABLE IF EXISTS %s CASCADE;', v_qualified);

    -- CREATE TABLE (columns copied from current catalog)
    SELECT
        'CREATE TABLE ' || v_qualified || E' (\n' ||
        string_agg(
            '    ' || quote_ident(a.attname) || ' ' ||
            pg_catalog.format_type(a.atttypid, a.atttypmod) ||
            CASE WHEN a.attnotnull THEN ' NOT NULL' ELSE '' END ||
            CASE
                WHEN ad.adbin IS NOT NULL THEN
                    ' DEFAULT ' || pg_get_expr(ad.adbin, ad.adrelid)
                ELSE ''
            END,
            E',\n' ORDER BY a.attnum
        ) ||
        E'\n);'
    INTO v_create
    FROM pg_catalog.pg_attribute a
    JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
    JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
    LEFT JOIN pg_catalog.pg_attrdef ad
        ON ad.adrelid = a.attrelid AND ad.adnum = a.attnum
    WHERE n.nspname = p_schema_name
      AND c.relname = p_table_name
      AND a.attnum > 0
      AND NOT a.attisdropped;

    IF v_create IS NULL THEN
        RAISE EXCEPTION 'Could not build CREATE TABLE for %.%', p_schema_name, p_table_name;
    END IF;

    -- Column list for INSERT statements
    SELECT string_agg(quote_ident(a.attname), ', ' ORDER BY a.attnum)
    INTO v_cols
    FROM pg_catalog.pg_attribute a
    JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
    JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
    WHERE n.nspname = p_schema_name
      AND c.relname = p_table_name
      AND a.attnum > 0
      AND NOT a.attisdropped;

    -- INSERT rows (values quoted from live data)
    FOR v_row IN EXECUTE format('SELECT * FROM %I.%I', p_schema_name, p_table_name)
    LOOP
        v_vals := NULL;

        FOR v_col IN
            SELECT a.attname
            FROM pg_catalog.pg_attribute a
            JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
            JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
            WHERE n.nspname = p_schema_name
              AND c.relname = p_table_name
              AND a.attnum > 0
              AND NOT a.attisdropped
            ORDER BY a.attnum
        LOOP
            EXECUTE format(
                'SELECT quote_nullable(($1).%I::text)',
                v_col.attname
            )
            USING v_row
            INTO v_val;

            IF v_vals IS NULL THEN
                v_vals := v_val;
            ELSE
                v_vals := v_vals || ', ' || v_val;
            END IF;
        END LOOP;

        v_inserts := v_inserts ||
            format('INSERT INTO %s (%s) VALUES (%s);', v_qualified, v_cols, v_vals) ||
            E'\n';
    END LOOP;

    -- Reset SERIAL / IDENTITY sequences after explicit inserts
    FOR v_col_name, v_seq_name IN
        SELECT
            a.attname,
            pg_get_serial_sequence(v_qualified, a.attname)
        FROM pg_catalog.pg_attribute a
        JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
        JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
        WHERE n.nspname = p_schema_name
          AND c.relname = p_table_name
          AND a.attnum > 0
          AND NOT a.attisdropped
          AND pg_get_serial_sequence(v_qualified, a.attname) IS NOT NULL
    LOOP
        v_sequences := v_sequences || format(
            'SELECT setval(%L, COALESCE((SELECT MAX(%I) FROM %s), 1), %s);',
            v_seq_name,
            v_col_name,
            v_qualified,
            CASE WHEN v_inserts = '' THEN 'false' ELSE 'true' END
        ) || E'\n';
    END LOOP;

    RETURN
        '-- Export of ' || v_qualified || E'\n' ||
        '-- Generated at ' || clock_timestamp()::TEXT || E'\n\n' ||
        v_drop || E'\n\n' ||
        v_create || E'\n\n' ||
        COALESCE(NULLIF(v_inserts, ''), '-- (no rows)' || E'\n') ||
        CASE
            WHEN v_sequences <> '' THEN E'\n' || v_sequences
            ELSE ''
        END;
END;
$$;

/*
Quick test in pgAdmin (source DB):

SELECT fn_export_table_script('users');

Export several tables (respect FK order: parents before children):

SELECT fn_export_table_script('users');
SELECT fn_export_table_script('email_accounts');
SELECT fn_export_table_script('emails');
SELECT fn_export_table_script('classifications');
SELECT fn_export_table_script('rules');

Paste each script into the target database Query Tool and run.
*/
