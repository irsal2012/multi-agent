"""
Command-line interface for the Multi-Agent Framework.
"""

import click
import json
import sys
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from core.pipeline import pipeline
from core.utils import setup_logging

console = Console()
logger = setup_logging()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Multi-Agent Framework - Transform ideas into complete Python applications."""
    pass

@cli.command()
@click.argument('description')
@click.option('--project-name', '-n', help='Project name (auto-generated if not provided)')
@click.option('--output-dir', '-o', default='output', help='Output directory for generated files')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def generate(description: str, project_name: Optional[str], output_dir: str, verbose: bool):
    """Generate a complete application from a description."""
    
    console.print(Panel.fit(
        "[bold blue]Multi-Agent Code Generator[/bold blue]\n"
        "Transforming your idea into a complete Python application...",
        border_style="blue"
    ))
    
    # Validate input
    validation = pipeline.validate_input(description)
    
    if validation['warnings']:
        console.print("\n[yellow]⚠️  Warnings:[/yellow]")
        for warning in validation['warnings']:
            console.print(f"  • {warning}")
    
    if validation['suggestions']:
        console.print("\n[cyan]💡 Suggestions:[/cyan]")
        for suggestion in validation['suggestions']:
            console.print(f"  • {suggestion}")
    
    # Confirm to proceed
    if not click.confirm("\nProceed with generation?"):
        console.print("[yellow]Generation cancelled.[/yellow]")
        return
    
    # Run pipeline with progress tracking
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            
            task = progress.add_task("Initializing agents...", total=None)
            
            # Update progress based on pipeline steps
            def update_progress_callback():
                status = pipeline.get_pipeline_status()
                current_progress = status['current_progress']
                
                if current_progress['steps']:
                    current_step = current_progress['current_step']
                    if current_step < len(current_progress['steps']):
                        step = current_progress['steps'][current_step]
                        progress.update(task, description=f"[cyan]{step['description']}[/cyan]")
            
            # Run the pipeline
            results = pipeline.run_pipeline(description, project_name)
            
            progress.update(task, description="[green]✅ Generation completed![/green]")
        
        # Display results
        display_cli_results(results, verbose)
        
    except Exception as e:
        console.print(f"\n[red]❌ Generation failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)

@cli.command()
def status():
    """Show pipeline status and statistics."""
    
    try:
        status = pipeline.get_pipeline_status()
        
        # Create status table
        table = Table(title="Pipeline Status", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Runs", str(status['total_runs']))
        table.add_row("Successful Runs", str(status['successful_runs']))
        table.add_row("Failed Runs", str(status['failed_runs']))
        
        if status['total_runs'] > 0:
            success_rate = (status['successful_runs'] / status['total_runs']) * 100
            table.add_row("Success Rate", f"{success_rate:.1f}%")
        
        console.print(table)
        
        # Current progress
        progress = status['current_progress']
        if progress['total_steps'] > 0:
            console.print(f"\n[bold]Current Progress:[/bold] {progress['progress_percentage']:.1f}%")
            
            for step in progress['steps']:
                status_icon = {
                    'pending': '⏳',
                    'running': '🔄',
                    'completed': '✅',
                    'failed': '❌'
                }.get(step['status'], '❓')
                
                console.print(f"{status_icon} {step['name']}: {step['description']}")
        
    except Exception as e:
        console.print(f"[red]Failed to get status: {str(e)}[/red]")

@cli.command()
def agents():
    """List available agents and their capabilities."""
    
    try:
        agent_info = pipeline.get_agent_info()
        
        console.print(Panel.fit(
            "[bold blue]Available Agents[/bold blue]",
            border_style="blue"
        ))
        
        # Pipeline steps
        console.print("\n[bold]Pipeline Steps:[/bold]")
        for i, step in enumerate(agent_info['pipeline_steps'], 1):
            console.print(f"  {i}. {step}")
        
        # Agent descriptions
        console.print("\n[bold]Agent Descriptions:[/bold]")
        for agent_key, description in agent_info['agent_descriptions'].items():
            agent_name = agent_key.replace('_', ' ').title()
            console.print(f"\n[cyan]🤖 {agent_name}[/cyan]")
            console.print(f"  {description}")
        
        # Available agents
        console.print(f"\n[bold]Loaded Agents:[/bold] {len(agent_info['available_agents'])}")
        for agent in agent_info['available_agents']:
            console.print(f"  ✅ {agent}")
            
    except Exception as e:
        console.print(f"[red]Failed to get agent info: {str(e)}[/red]")

@cli.command()
@click.option('--limit', '-l', default=10, help='Number of recent projects to show')
def history(limit: int):
    """Show project generation history."""
    
    try:
        status = pipeline.get_pipeline_status()
        history_data = status['pipeline_history']
        
        if not history_data:
            console.print("[yellow]No projects generated yet.[/yellow]")
            return
        
        # Show recent projects
        recent_projects = list(reversed(history_data))[:limit]
        
        table = Table(title=f"Recent Projects (Last {len(recent_projects)})", show_header=True)
        table.add_column("Project", style="cyan")
        table.add_column("Timestamp", style="dim")
        table.add_column("Status", style="green")
        table.add_column("Time", style="yellow")
        table.add_column("Description", style="white", max_width=50)
        
        for project in recent_projects:
            status_icon = "✅" if project['success'] else "❌"
            description = project['user_input'][:47] + "..." if len(project['user_input']) > 50 else project['user_input']
            
            table.add_row(
                project['project_name'],
                project['timestamp'][:19],  # Remove microseconds
                status_icon,
                f"{project['execution_time']:.1f}s",
                description
            )
        
        console.print(table)
        
        # Summary
        total = len(history_data)
        successful = sum(1 for h in history_data if h['success'])
        avg_time = sum(h['execution_time'] for h in history_data) / total
        
        console.print(f"\n[bold]Summary:[/bold] {total} total projects, {successful} successful ({successful/total*100:.1f}%), avg time: {avg_time:.1f}s")
        
    except Exception as e:
        console.print(f"[red]Failed to get history: {str(e)}[/red]")

@cli.command()
@click.option('--host', default='localhost', help='Host to run on')
@click.option('--port', default=8501, help='Port to run on')
def web(host: str, port: int):
    """Launch the Streamlit web interface."""
    
    console.print(Panel.fit(
        "[bold blue]Launching Web Interface[/bold blue]\n"
        f"Starting Streamlit server on http://{host}:{port}",
        border_style="blue"
    ))
    
    import subprocess
    import sys
    
    try:
        # Launch Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.address", host,
            "--server.port", str(port),
            "--server.headless", "true"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Web interface stopped.[/yellow]")
    except Exception as e:
        console.print(f"[red]Failed to start web interface: {str(e)}[/red]")

def display_cli_results(results: dict, verbose: bool = False):
    """Display generation results in the CLI."""
    
    console.print("\n" + "="*60)
    console.print(Panel.fit(
        f"[bold green]✅ Generation Completed Successfully![/bold green]\n"
        f"Project: {results['project_name']}\n"
        f"Time: {results['pipeline_metadata']['execution_time_seconds']:.1f}s",
        border_style="green"
    ))
    
    # Show generated components
    console.print("\n[bold]Generated Components:[/bold]")
    
    components = [
        ("📋 Requirements", "requirements"),
        ("💻 Code", "code"),
        ("📚 Documentation", "documentation"),
        ("🧪 Tests", "tests"),
        ("🚀 Deployment", "deployment"),
        ("🎨 UI", "ui")
    ]
    
    for icon_name, key in components:
        if key in results and results[key]:
            console.print(f"  ✅ {icon_name}")
        else:
            console.print(f"  ❌ {icon_name}")
    
    # Show code preview if verbose
    if verbose and 'code' in results and 'final_code' in results['code']:
        console.print("\n[bold]Generated Code Preview:[/bold]")
        code = results['code']['final_code']
        
        # Show first 20 lines
        lines = code.split('\n')[:20]
        preview = '\n'.join(lines)
        if len(code.split('\n')) > 20:
            preview += '\n... (truncated)'
        
        syntax = Syntax(preview, "python", theme="monokai", line_numbers=True)
        console.print(syntax)
    
    # Show file locations
    console.print(f"\n[bold]Output saved to:[/bold] output/{results['project_name']}_*")
    console.print("\n[cyan]💡 Tip: Use 'python main.py web' to launch the web interface for better visualization.[/cyan]")

if __name__ == "__main__":
    cli()
