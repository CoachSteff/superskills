"""
Progress indicators for long-running tasks.
"""
from typing import Optional

from rich.console import Console
from rich.live import Live
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.spinner import Spinner

console = Console()


class ProgressIndicator:
    """Progress indicator for skill and workflow execution."""

    def __init__(self, show_progress: bool = True):
        self.show_progress = show_progress
        self._progress: Optional[Progress] = None
        self._task_id: Optional[int] = None

    def spinner(self, message: str):
        """
        Show a spinner with a message.

        Usage:
            with progress.spinner("Processing..."):
                # do work
        """
        if not self.show_progress:
            return NullContext()

        return Live(
            Spinner("dots", text=message),
            console=console,
            transient=True
        )

    def create_workflow_progress(self, total_steps: int, description: str = "Workflow"):
        """
        Create a progress bar for workflow execution.

        Args:
            total_steps: Total number of steps in the workflow
            description: Description to show

        Returns:
            Progress context manager
        """
        if not self.show_progress:
            return NullProgressContext()

        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console
        )

        self._task_id = self._progress.add_task(description, total=total_steps)

        return WorkflowProgressContext(self._progress, self._task_id)

    def update_workflow_progress(self, step: int, message: str):
        """
        Update workflow progress.

        Args:
            step: Current step number (1-indexed)
            message: Message to display
        """
        if self._progress and self._task_id is not None:
            self._progress.update(
                self._task_id,
                completed=step,
                description=f"[bold blue]{message}"
            )

    def finish_workflow_progress(self):
        """Mark workflow as complete."""
        if self._progress and self._task_id is not None:
            self._progress.update(
                self._task_id,
                completed=self._progress.tasks[self._task_id].total
            )


class WorkflowProgressContext:
    """Context manager for workflow progress."""

    def __init__(self, progress: Progress, task_id: int):
        self.progress = progress
        self.task_id = task_id

    def __enter__(self):
        self.progress.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.progress.__exit__(exc_type, exc_val, exc_tb)

    def update(self, completed: int, description: Optional[str] = None):
        """Update progress."""
        kwargs = {'completed': completed}
        if description:
            kwargs['description'] = f"[bold blue]{description}"
        self.progress.update(self.task_id, **kwargs)


class NullContext:
    """Null context manager that does nothing."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class NullProgressContext:
    """Null progress context that does nothing."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def update(self, completed: int, description: Optional[str] = None):
        """No-op update."""
        pass
