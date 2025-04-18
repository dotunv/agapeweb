# Database Migrations Versioning Strategy

This document outlines the strategy for managing database migrations in the Agape project.

## Overview

Database migrations are a critical part of application development and deployment. They need to be:

- **Versioned**: Each migration should have a unique identifier
- **Ordered**: Migrations should be applied in the correct order
- **Documented**: Changes should be well-documented
- **Tested**: Migrations should be tested before deployment
- **Reversible**: Migrations should be reversible when possible

## Migration Naming Convention

All migrations should follow this naming convention:

```
YYYYMMDDHHMM_descriptive_name.py
```

Where:
- `YYYYMMDDHHMM` is the timestamp (year, month, day, hour, minute)
- `descriptive_name` is a brief description of what the migration does

Example: `202305151423_add_user_profile_fields.py`

This naming convention ensures that:
1. Migrations are applied in chronological order
2. The name gives a clear indication of what the migration does
3. There are no conflicts when multiple developers create migrations

## Migration Management Script

We've created a script to help manage migrations: `scripts/manage_migrations.py`

### Usage

```bash
# Check for unapplied migrations
python scripts/manage_migrations.py check

# Generate a migration plan
python scripts/manage_migrations.py plan

# Create a new migration with proper naming
python scripts/manage_migrations.py make <app_name> <migration_name>

# Generate a visualization of migration dependencies
python scripts/manage_migrations.py graph

# Squash migrations
python scripts/manage_migrations.py squash <app_name> <start_migration> <end_migration>
```

### Creating Migrations

When creating a new migration, use the `make` command:

```bash
python scripts/manage_migrations.py make users add_profile_fields
```

This will create a migration with a timestamp prefix, e.g., `users/migrations/202305151423_add_profile_fields.py`.

After creating a migration, remember to:
1. Review the migration file to ensure it's correct
2. Add a detailed docstring explaining the changes
3. Run tests to verify the migration works as expected
4. Update the migration documentation if necessary

### Migration Documentation

Each migration file should include a detailed docstring explaining:
- What changes are being made
- Why the changes are necessary
- Any dependencies or prerequisites
- Any post-migration steps that might be needed

Example:

```python
"""
Add profile fields to User model.

This migration adds the following fields to the User model:
- bio: TextField for user biography
- birth_date: DateField for user's birth date
- location: CharField for user's location

These fields are needed to support the new user profile feature.
"""
```

## Migration Workflow

1. **Development**:
   - Create migrations using the `make` command
   - Test migrations locally
   - Document changes

2. **Code Review**:
   - Review migration files
   - Ensure proper documentation
   - Verify tests

3. **Staging**:
   - Apply migrations to staging environment
   - Verify functionality
   - Test rollback if necessary

4. **Production**:
   - Apply migrations during maintenance window
   - Monitor for issues
   - Have rollback plan ready

## Handling Conflicts

If multiple developers create migrations that conflict:

1. Determine which migration should be applied first
2. Rename the other migration with a later timestamp
3. Adjust dependencies if necessary
4. Test the migrations to ensure they work correctly

## Squashing Migrations

When the number of migrations becomes unwieldy, consider squashing them:

```bash
python scripts/manage_migrations.py squash users 0001 0010
```

This will combine migrations 0001 through 0010 into a single migration.

After squashing:
1. Review the squashed migration
2. Test it thoroughly
3. Update documentation
4. Deploy to staging before production

## Visualizing Migrations

To understand the dependencies between migrations, use the `graph` command:

```bash
python scripts/manage_migrations.py graph
```

This will generate a PNG file showing the migration graph.

## Best Practices

1. **Keep migrations small and focused**
2. **Always test migrations before deployment**
3. **Document all changes thoroughly**
4. **Make migrations reversible when possible**
5. **Use data migrations for complex data transformations**
6. **Be cautious with schema changes to large tables**
7. **Consider database performance during migrations**
8. **Have a rollback plan for every migration**