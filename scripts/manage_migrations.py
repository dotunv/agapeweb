#!/usr/bin/env python
"""
Migration management script for the Agape project.

This script provides utilities for managing database migrations, including:
- Checking for unapplied migrations
- Generating migration plans
- Creating migrations with proper naming conventions
- Visualizing migration dependencies
- Squashing migrations

Usage:
    python scripts/manage_migrations.py check
    python scripts/manage_migrations.py plan
    python scripts/manage_migrations.py make <app_name> <migration_name>
    python scripts/manage_migrations.py graph
    python scripts/manage_migrations.py squash <app_name> <start_migration> <end_migration>
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agape.settings')

import django
django.setup()

from django.core.management import call_command
from django.db.migrations.loader import MigrationLoader
from django.db import connections

def check_migrations():
    """Check for unapplied migrations."""
    print("Checking for unapplied migrations...")
    call_command('showmigrations')
    
    # Check if there are any unapplied migrations
    loader = MigrationLoader(connections['default'])
    unapplied = []
    
    for app_name, migration_name in loader.graph.leaf_nodes():
        if (app_name, migration_name) not in loader.applied_migrations:
            unapplied.append((app_name, migration_name))
    
    if unapplied:
        print("\nUnapplied migrations:")
        for app_name, migration_name in unapplied:
            print(f"  {app_name}: {migration_name}")
        print("\nRun 'python manage.py migrate' to apply these migrations.")
    else:
        print("\nAll migrations have been applied.")

def plan_migrations():
    """Generate a migration plan."""
    print("Generating migration plan...")
    call_command('migrate', plan=True)

def make_migration(app_name, migration_name):
    """Create a new migration with proper naming conventions."""
    # Get the current timestamp for versioning
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    
    # Format the migration name with timestamp prefix
    full_name = f"{timestamp}_{migration_name}"
    
    print(f"Creating migration {full_name} for {app_name}...")
    call_command('makemigrations', app_name, name=full_name)
    
    print("\nMigration created. Remember to:")
    print("1. Review the migration file to ensure it's correct")
    print("2. Add a detailed docstring explaining the changes")
    print("3. Run tests to verify the migration works as expected")
    print("4. Update the migration documentation if necessary")

def generate_graph():
    """Generate a visualization of migration dependencies."""
    print("Generating migration graph...")
    try:
        call_command('graph_migrations', all_apps=True, output='migration_graph.png')
        print("Migration graph generated: migration_graph.png")
    except Exception as e:
        print(f"Error generating migration graph: {e}")
        print("Make sure graphviz is installed on your system.")
        print("On Ubuntu/Debian: sudo apt-get install graphviz")
        print("On macOS: brew install graphviz")
        print("On Windows: Install from https://graphviz.org/download/")

def squash_migrations(app_name, start_migration, end_migration):
    """Squash a range of migrations."""
    print(f"Squashing migrations for {app_name} from {start_migration} to {end_migration}...")
    call_command('squashmigrations', app_name, start_migration, end_migration)
    
    print("\nMigrations squashed. Remember to:")
    print("1. Review the squashed migration file")
    print("2. Update the migration documentation")
    print("3. Test the squashed migration in a development environment before deploying")

def main():
    parser = argparse.ArgumentParser(description='Manage database migrations for the Agape project.')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Check command
    subparsers.add_parser('check', help='Check for unapplied migrations')
    
    # Plan command
    subparsers.add_parser('plan', help='Generate a migration plan')
    
    # Make command
    make_parser = subparsers.add_parser('make', help='Create a new migration')
    make_parser.add_argument('app_name', help='Name of the app to create migration for')
    make_parser.add_argument('migration_name', help='Name of the migration')
    
    # Graph command
    subparsers.add_parser('graph', help='Generate a visualization of migration dependencies')
    
    # Squash command
    squash_parser = subparsers.add_parser('squash', help='Squash a range of migrations')
    squash_parser.add_argument('app_name', help='Name of the app to squash migrations for')
    squash_parser.add_argument('start_migration', help='Start migration name or number')
    squash_parser.add_argument('end_migration', help='End migration name or number')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        check_migrations()
    elif args.command == 'plan':
        plan_migrations()
    elif args.command == 'make':
        make_migration(args.app_name, args.migration_name)
    elif args.command == 'graph':
        generate_graph()
    elif args.command == 'squash':
        squash_migrations(args.app_name, args.start_migration, args.end_migration)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()