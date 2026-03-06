"""
Template loader for Jinja2 templates in the facts package.

Uses importlib.resources to load templates from package data with
fallback to filesystem paths for development.
"""
from pathlib import Path

import jinja2

# Try to use importlib.resources (3.9+) with proper versioning
try:
    from importlib.resources import files, as_file
except ImportError:
    # Fallback for Python < 3.9
    from importlib_resources import files, as_file


def get_template_loader() -> jinja2.Environment:
    """
    Create and return a Jinja2 environment configured with the facts templates.

    Returns a FileSystemLoader that points to the templates directory, with
    fallback to local filesystem paths for development.

    Returns:
        jinja2.Environment: Configured Jinja2 environment ready to render templates
    """
    # Try to get templates from package resources first (works for installed packages)
    try:
        template_files = files("facts").joinpath("templates")
        with as_file(template_files) as template_dir:
            loader = jinja2.FileSystemLoader(str(template_dir))
            return jinja2.Environment(loader=loader)
    except (ModuleNotFoundError, TypeError):
        pass

    # Fallback for development: templates should be adjacent to this file
    template_path = Path(__file__).parent / "templates"
    if template_path.is_dir():
        loader = jinja2.FileSystemLoader(str(template_path))
        return jinja2.Environment(loader=loader)

    # If no templates directory found, raise helpful error
    raise RuntimeError(
        f"Could not find templates directory. Expected at: {template_path}"
    )


def render_template(template_name: str, **context) -> str:
    """
    Render a Jinja2 template by name.

    Args:
        template_name: Name of the template file (e.g., 'dns_zone_records.jinja2')
        **context: Context variables to pass to the template

    Returns:
        str: Rendered template content
    """
    env = get_template_loader()
    template = env.get_template(template_name)
    return template.render(**context)
