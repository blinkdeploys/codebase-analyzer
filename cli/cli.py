#!/usr/bin/env python3
import click
import sys
import os
from pathlib import Path
sys.path.append('/app')
from worker.worker import CodebaseAnalyzer



@click.group()
def cli():
    """Codebase Analyzer CLI - Reconstruct codebases with logical Git structure"""
    pass


@cli.command()
@click.argument('repo_path', type=click.Path(exists=True))
@click.argument('output_name')
@click.option('--description', '-d', help='Optional project description')
def analyze(repo_path, output_name, description):
    """
    Analyze a codebase and recreate it with logical Git structure.
    
    REPO_PATH: Path to the codebase to analyze
    OUTPUT_NAME: Name for the output repository
    """
    pass


@cli.command()
@click.argument('repo_path', type=click.Path(exists=True))
def inspect(repo_path):
    """
    Quick inspection of a codebase without creating output.
    Shows what features would be identified.
    """
    pass


@cli.command()
def version():
    """Show version information"""
    click.echo("Codebase Analyzer CLI v1.0.0")
    click.echo("AI Assisted")


if __name__ == '__main__':
    cli()

