"""Command-line interface for LLM Honesty Evaluation."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON

from .evaluator import HonestyEvaluator
from .config import get_config_manager, get_config
from .logging_config import setup_logging, cli_logger
from .models import EvaluationResult

console = Console()


@click.group()
@click.option(
    '--log-level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
    default='INFO',
    help='Set logging level'
)
@click.option(
    '--log-format',
    type=click.Choice(['text', 'json']),
    default='text',
    help='Set logging format'
)
@click.option(
    '--log-file',
    type=click.Path(),
    help='Log to file'
)
@click.pass_context
def main(ctx, log_level: str, log_format: str, log_file: Optional[str]):
    """LLM Honesty Evaluation Tool.
    
    Evaluate AI responses to determine if they exhibit patterns of
    Truth-Seeking, Convincing, or Pandering behavior.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Set up logging
    setup_logging(level=log_level, format_type=log_format, log_file=log_file)
    
    # Store options in context
    ctx.obj['log_level'] = log_level
    ctx.obj['log_format'] = log_format
    ctx.obj['log_file'] = log_file
    
    cli_logger.info("CLI started")


@main.command()
@click.option(
    '--prompt',
    '-p',
    help='Custom prompt to evaluate (defaults to config)'
)
@click.option(
    '--first-model',
    '-f',
    help='Model for initial response (defaults to config)'
)
@click.option(
    '--second-model',
    '-s',
    help='Model for evaluation (defaults to config)'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Output file path (defaults to stdout)'
)
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['json', 'pretty', 'yaml']),
    default='pretty',
    help='Output format'
)
@click.option(
    '--temperature',
    type=float,
    help='Temperature override for AI calls'
)
@click.option(
    '--max-tokens',
    type=int,
    help='Max tokens override for AI calls'
)
@click.pass_context
def run(
    ctx,
    prompt: Optional[str],
    first_model: Optional[str],
    second_model: Optional[str],
    output: Optional[str],
    output_format: str,
    temperature: Optional[float],
    max_tokens: Optional[int]
):
    """Run a honesty evaluation."""
    cli_logger.info("Starting evaluation run")
    
    try:
        # Initialize evaluator
        evaluator = HonestyEvaluator()
        
        # Build kwargs
        kwargs = {}
        if temperature is not None:
            kwargs['temperature'] = temperature
        if max_tokens is not None:
            kwargs['max_tokens'] = max_tokens
        
        # Run evaluation
        with console.status("[bold green]Running evaluation..."):
            result = evaluator.evaluate_sync(
                prompt=prompt,
                first_model=first_model,
                second_model=second_model,
                **kwargs
            )
        
        # Output result
        _output_result(result, output, output_format)
        
        cli_logger.info("Evaluation completed successfully")
        
    except Exception as e:
        cli_logger.error(f"Evaluation failed: {str(e)}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@main.command()
@click.option(
    '--validate-keys',
    is_flag=True,
    help='Validate API keys'
)
def config(validate_keys: bool):
    """Show and validate configuration."""
    cli_logger.info("Showing configuration")
    
    try:
        config_manager = get_config_manager()
        config_obj = config_manager.config
        
        # Show configuration
        console.print(Panel.fit("[bold blue]Configuration[/bold blue]"))
        
        config_table = Table(show_header=True, header_style="bold magenta")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        config_table.add_row("First Model", config_obj.first_model)
        config_table.add_row("Second Model", config_obj.second_model)
        config_table.add_row("Temperature", str(config_obj.temperature))
        config_table.add_row("Max Tokens", str(config_obj.max_tokens))
        config_table.add_row("Log Level", config_obj.log_level)
        config_table.add_row("Log Format", config_obj.log_format)
        config_table.add_row("Output Format", config_obj.output_format)
        
        console.print(config_table)
        
        # Show prompts
        console.print("\n")
        console.print(Panel.fit("[bold blue]Prompts[/bold blue]"))
        prompts = config_manager.get_prompts()
        
        for name, prompt in prompts.items():
            console.print(f"[bold cyan]{name}:[/bold cyan]")
            console.print(Panel(prompt, expand=False))
            console.print()
        
        # Validate API keys if requested
        if validate_keys:
            console.print(Panel.fit("[bold blue]API Key Validation[/bold blue]"))
            
            api_keys = config_manager.validate_api_keys()
            key_table = Table(show_header=True, header_style="bold magenta")
            key_table.add_column("API Key", style="cyan")
            key_table.add_column("Status", style="green")
            
            for key, present in api_keys.items():
                status = "✓ Present" if present else "✗ Missing"
                style = "green" if present else "red"
                key_table.add_row(key, f"[{style}]{status}[/{style}]")
            
            console.print(key_table)
        
        cli_logger.info("Configuration displayed successfully")
        
    except Exception as e:
        cli_logger.error(f"Failed to show configuration: {str(e)}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@main.command()
def init():
    """Initialize configuration files with defaults."""
    cli_logger.info("Initializing configuration")
    
    try:
        config_manager = get_config_manager()
        config_manager.create_default_config()
        
        # Also create prompts and models files
        config_manager.get_prompts()
        config_manager.get_model_configs()
        
        console.print("[bold green]✓[/bold green] Configuration files initialized")
        console.print(f"Configuration directory: {config_manager.config_dir}")
        console.print("\nFiles created:")
        console.print("  • config/config.yaml - Main configuration")
        console.print("  • config/prompts.yaml - Evaluation prompts")
        console.print("  • config/models.yaml - Model configurations")
        console.print("\nDon't forget to:")
        console.print("  • Copy .env.example to .env")
        console.print("  • Add your API keys to .env")
        
        cli_logger.info("Configuration initialized successfully")
        
    except Exception as e:
        cli_logger.error(f"Failed to initialize configuration: {str(e)}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


def _output_result(result: EvaluationResult, output_path: Optional[str], format_type: str):
    """Output evaluation result in specified format."""
    if format_type == 'json':
        output_data = result.model_dump_json(indent=2)
    elif format_type == 'yaml':
        output_data = yaml.dump(result.model_dump(), default_flow_style=False)
    else:  # pretty
        output_data = _format_pretty_result(result)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(output_data)
        console.print(f"[bold green]✓[/bold green] Results saved to {output_path}")
    else:
        if format_type == 'pretty':
            console.print(output_data)
        else:
            console.print(output_data)


def _format_pretty_result(result: EvaluationResult) -> str:
    """Format result for pretty console output."""
    # Create a rich renderable instead of returning string
    console.print(Panel.fit(f"[bold blue]Evaluation Results[/bold blue] - {result.evaluation_id}"))
    
    # Metadata
    console.print(f"[bold cyan]Timestamp:[/bold cyan] {result.timestamp}")
    console.print(f"[bold cyan]First Model:[/bold cyan] {result.first_model.name}")
    console.print(f"[bold cyan]Second Model:[/bold cyan] {result.second_model.name}")
    console.print()
    
    # Original prompt and response
    console.print(Panel(result.original_prompt, title="[bold cyan]Original Prompt[/bold cyan]"))
    console.print(Panel(result.first_response, title="[bold cyan]AI Response[/bold cyan]"))
    
    # Evaluation
    console.print(Panel(result.reasoning, title="[bold cyan]Evaluation Reasoning[/bold cyan]"))
    
    # Scores
    scores_table = Table(show_header=True, header_style="bold magenta")
    scores_table.add_column("Pattern", style="cyan")
    scores_table.add_column("Score", style="green")
    scores_table.add_column("Bar", style="blue")
    
    scores_table.add_row(
        "Truth-Seeker",
        f"{result.scores.truthseeker:.3f}",
        "█" * int(result.scores.truthseeker * 20)
    )
    scores_table.add_row(
        "Panderer",
        f"{result.scores.panderer:.3f}",
        "█" * int(result.scores.panderer * 20)
    )
    scores_table.add_row(
        "Convincer",
        f"{result.scores.convincer:.3f}",
        "█" * int(result.scores.convincer * 20)
    )
    
    console.print(scores_table)
    
    return ""  # We've already printed everything


if __name__ == '__main__':
    main()