
-- Create Roles
DO $$
BEGIN
    IF NOT EXISTS (SELECT * FROM pg_catalog.pg_roles WHERE rolname = 'migrate') THEN
      CREATE ROLE "migrate";
   END IF;

   IF NOT EXISTS (SELECT * FROM pg_catalog.pg_roles WHERE rolname = 'web') THEN
      CREATE ROLE "web";
   END IF;

   IF NOT EXISTS (SELECT * FROM pg_catalog.pg_roles WHERE rolname = 'dev-web') THEN
      CREATE ROLE "dev-web";
   END IF;

   IF NOT EXISTS (SELECT * FROM pg_catalog.pg_roles WHERE rolname = 'azure_pg_admin') THEN
      CREATE ROLE "azure_pg_admin";
   END IF;

END
$$;


-- Create Extensions
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_buffercache";

