"""
EmailCampaigner.py - Email campaign management using SendGrid.
"""
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Content, Email, Mail, To
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    print("Warning: sendgrid not available - install with: pip install sendgrid")

try:
    from jinja2 import Environment, FileSystemLoader, Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    print("Warning: jinja2 not available - install with: pip install jinja2")


@dataclass
class EmailResult:
    """Result from an email operation."""
    recipient: str
    subject: str
    status: str
    message_id: str = ""
    error: str = ""
    sent_at: str = None
    timestamp: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.sent_at:
            self.sent_at = datetime.now().isoformat()


class EmailCampaigner:
    """Email campaign management using SendGrid."""

    def __init__(
        self,
        output_dir: str = "output/emails",
        templates_dir: str = "templates/email",
        verbose: bool = True
    ):
        """Initialize EmailCampaigner.

        Args:
            output_dir: Directory to save email logs
            templates_dir: Directory containing email templates
            verbose: Enable verbose logging
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        self.verbose = verbose

        if not SENDGRID_AVAILABLE:
            raise ImportError("sendgrid is required. Install with: pip install sendgrid")

        if not JINJA2_AVAILABLE:
            raise ImportError("jinja2 is required. Install with: pip install jinja2")

        # Validate environment variable
        self.api_key = os.getenv("SENDGRID_API_KEY")
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY environment variable not set")

        self.client = SendGridAPIClient(self.api_key)
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_dir)))

    def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        from_email: Optional[str] = None,
        content_type: Literal["text/plain", "text/html"] = "text/html",
        template_data: Optional[Dict] = None
    ) -> EmailResult:
        """Send a single email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            content: Email content (plain text or HTML)
            from_email: Sender email (defaults to verified sender)
            content_type: Content type (text/plain or text/html)
            template_data: Data to render template (if content is template)

        Returns:
            EmailResult with send status
        """
        if self.verbose:
            print(f"Sending email to: {to_email}")

        # Render template if template_data provided
        if template_data:
            try:
                template = Template(content)
                content = template.render(**template_data)
            except Exception as e:
                return EmailResult(
                    recipient=to_email,
                    subject=subject,
                    status="failed",
                    error=f"Template rendering error: {str(e)}"
                )

        # Create message
        from_addr = from_email or os.getenv("SENDGRID_FROM_EMAIL", "noreply@example.com")
        message = Mail(
            from_email=Email(from_addr),
            to_emails=To(to_email),
            subject=subject,
            html_content=Content(content_type, content)
        )

        try:
            response = self.client.send(message)

            result = EmailResult(
                recipient=to_email,
                subject=subject,
                status="sent",
                message_id=response.headers.get("X-Message-Id", "")
            )

            if self.verbose:
                print(f"✓ Email sent to {to_email}")

            self._log_email(result)
            return result

        except Exception as e:
            result = EmailResult(
                recipient=to_email,
                subject=subject,
                status="failed",
                error=str(e)
            )

            if self.verbose:
                print(f"✗ Failed to send to {to_email}: {e}")

            self._log_email(result)
            return result

    def send_campaign(
        self,
        recipients: List[str],
        subject: str,
        content: str,
        from_email: Optional[str] = None,
        personalization: Optional[Dict[str, Dict]] = None
    ) -> List[EmailResult]:
        """Send email campaign to multiple recipients.

        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            content: Email content template
            from_email: Sender email
            personalization: Dict mapping email to personalization data

        Returns:
            List of EmailResult objects
        """
        if self.verbose:
            print(f"Sending campaign to {len(recipients)} recipients")

        results = []
        personalization = personalization or {}

        for i, recipient in enumerate(recipients, 1):
            if self.verbose:
                print(f"[{i}/{len(recipients)}] Sending to {recipient}")

            # Get personalization data for this recipient
            template_data = personalization.get(recipient, {})
            template_data.setdefault("email", recipient)

            result = self.send_email(
                to_email=recipient,
                subject=subject,
                content=content,
                from_email=from_email,
                template_data=template_data
            )
            results.append(result)

        successful = sum(1 for r in results if r.status == "sent")
        if self.verbose:
            print(f"✓ Campaign complete: {successful}/{len(recipients)} sent")

        return results

    def schedule_drip(
        self,
        recipients: List[str],
        drip_sequence: List[Dict[str, str]],
        from_email: Optional[str] = None
    ) -> Dict[str, List[EmailResult]]:
        """Schedule a drip email sequence.

        Args:
            recipients: List of recipient email addresses
            drip_sequence: List of email dicts with 'subject', 'content', 'delay_days'
            from_email: Sender email

        Returns:
            Dict mapping sequence step to EmailResult list
        """
        if self.verbose:
            print(f"Scheduling {len(drip_sequence)}-email drip for {len(recipients)} recipients")

        all_results = {}

        for i, email_config in enumerate(drip_sequence, 1):
            step_key = f"email_{i}"
            subject = email_config.get("subject", "")
            email_config.get("content", "")
            delay_days = email_config.get("delay_days", 0)

            if self.verbose:
                print(f"\nStep {i}: {subject} (delay: {delay_days} days)")

            # In a real implementation, this would schedule emails
            # For now, we just log the configuration
            results = []
            for recipient in recipients:
                result = EmailResult(
                    recipient=recipient,
                    subject=subject,
                    status="scheduled",
                    message_id=f"drip_{i}_{recipient}"
                )
                results.append(result)

            all_results[step_key] = results

            if self.verbose:
                print(f"✓ Scheduled for {len(recipients)} recipients")

        # Save drip campaign configuration
        self._save_drip_config(recipients, drip_sequence, all_results)

        return all_results

    def create_template(
        self,
        template_name: str,
        content: str,
        variables: Optional[List[str]] = None
    ) -> str:
        """Create and save an email template.

        Args:
            template_name: Template filename (without extension)
            content: Template content with Jinja2 variables
            variables: List of variable names used in template

        Returns:
            Path to created template file
        """
        if self.verbose:
            print(f"Creating template: {template_name}")

        template_file = self.templates_dir / f"{template_name}.html"

        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # Save template metadata
        metadata_file = self.templates_dir / f"{template_name}.json"
        metadata = {
            "name": template_name,
            "variables": variables or [],
            "created_at": datetime.now().isoformat()
        }

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        if self.verbose:
            print(f"✓ Template created: {template_file}")

        return str(template_file)

    def load_template(
        self,
        template_name: str,
        template_data: Dict
    ) -> str:
        """Load and render a template.

        Args:
            template_name: Template filename (without extension)
            template_data: Data to render template

        Returns:
            Rendered template content
        """
        try:
            template = self.jinja_env.get_template(f"{template_name}.html")
            return template.render(**template_data)
        except Exception as e:
            raise RuntimeError(f"Failed to load template {template_name}: {e}")

    def _log_email(self, result: EmailResult):
        """Log email send result."""
        log_file = self.output_dir / f"email_log_{datetime.now().strftime('%Y%m%d')}.jsonl"

        log_entry = {
            "recipient": result.recipient,
            "subject": result.subject,
            "status": result.status,
            "message_id": result.message_id,
            "error": result.error,
            "sent_at": result.sent_at,
            "timestamp": result.timestamp
        }

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _save_drip_config(
        self,
        recipients: List[str],
        sequence: List[Dict],
        results: Dict[str, List[EmailResult]]
    ):
        """Save drip campaign configuration."""
        config_file = self.output_dir / f"drip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        config = {
            "recipients": recipients,
            "sequence": sequence,
            "scheduled_at": datetime.now().isoformat(),
            "results": {
                step: [
                    {
                        "recipient": r.recipient,
                        "subject": r.subject,
                        "status": r.status
                    }
                    for r in results_list
                ]
                for step, results_list in results.items()
            }
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        if self.verbose:
            print(f"✓ Drip config saved to: {config_file}")


def send_simple_email(
    to_email: str,
    subject: str,
    content: str,
    **kwargs
) -> EmailResult:
    """Convenience function to send a single email.

    Args:
        to_email: Recipient email
        subject: Email subject
        content: Email content
        **kwargs: Additional arguments for EmailCampaigner

    Returns:
        EmailResult
    """
    campaigner = EmailCampaigner()
    return campaigner.send_email(to_email, subject, content, **kwargs)
