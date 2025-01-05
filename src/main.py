import click
from html_fragmenter.msg_split import split_message

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--max-len', default=4096, help='Maximum length of each fragment')
def main(input_file: str, max_len: int):
    """Split HTML message from INPUT_FILE into fragments."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()
            
        for i, fragment in enumerate(split_message(source, max_len), 1):
            click.echo(f"-- fragment #{i}: {len(fragment)} chars --")
            click.echo(fragment)
            click.echo()
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    main()
