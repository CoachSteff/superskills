"""
Invoicer.py - Invoice generation and management using reportlab.
"""
import os
from typing import Dict, List, Optional, Literal
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not available - install with: pip install reportlab")


@dataclass
class InvoiceResult:
    """Result from an invoice operation."""
    invoice_number: str
    client_name: str
    total_amount: float
    currency: str
    status: str
    output_file: str = ""
    due_date: str = ""
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class Invoicer:
    """Invoice generation and management using reportlab."""
    
    def __init__(
        self,
        output_dir: str = "output/invoices",
        company_name: Optional[str] = None,
        company_address: Optional[str] = None,
        company_email: Optional[str] = None,
        verbose: bool = True
    ):
        """Initialize Invoicer.
        
        Args:
            output_dir: Directory to save invoices
            company_name: Your company name
            company_address: Your company address
            company_email: Your company email
            verbose: Enable verbose logging
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required. Install with: pip install reportlab")
        
        self.company_name = company_name or "Your Company Name"
        self.company_address = company_address or "Your Company Address"
        self.company_email = company_email or "contact@yourcompany.com"
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Invoice tracking
        self.invoice_db = self.output_dir / "invoices.json"
        self._load_invoice_db()
    
    def _setup_custom_styles(self):
        """Setup custom PDF styles."""
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1f4e79'),
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2e75b6'),
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT
        ))
    
    def _load_invoice_db(self):
        """Load invoice database."""
        if self.invoice_db.exists():
            with open(self.invoice_db, 'r') as f:
                self.invoices = json.load(f)
        else:
            self.invoices = []
    
    def _save_invoice_db(self):
        """Save invoice database."""
        with open(self.invoice_db, 'w') as f:
            json.dump(self.invoices, f, indent=2)
    
    def _generate_invoice_number(self) -> str:
        """Generate next invoice number."""
        if not self.invoices:
            return "INV-0001"
        
        last_number = max(
            int(inv['invoice_number'].split('-')[1])
            for inv in self.invoices
        )
        return f"INV-{last_number + 1:04d}"
    
    def create_invoice(
        self,
        client_name: str,
        client_address: str,
        client_email: str,
        line_items: List[Dict[str, any]],
        invoice_date: Optional[datetime] = None,
        due_days: int = 30,
        currency: str = "USD",
        tax_rate: float = 0.0,
        notes: Optional[str] = None,
        output_name: Optional[str] = None
    ) -> InvoiceResult:
        """Create an invoice.
        
        Args:
            client_name: Client name
            client_address: Client address
            client_email: Client email
            line_items: List of dicts with 'description', 'quantity', 'unit_price'
            invoice_date: Invoice date (defaults to today)
            due_days: Payment due in days
            currency: Currency code (USD, EUR, etc.)
            tax_rate: Tax rate (e.g., 0.1 for 10%)
            notes: Additional notes
            output_name: Output filename
            
        Returns:
            InvoiceResult with invoice details
        """
        invoice_date = invoice_date or datetime.now()
        due_date = invoice_date + timedelta(days=due_days)
        invoice_number = self._generate_invoice_number()
        
        if self.verbose:
            print(f"Creating invoice {invoice_number} for {client_name}")
        
        output_file = self.output_dir / (output_name or f"{invoice_number}.pdf")
        
        # Calculate totals
        subtotal = sum(
            item['quantity'] * item['unit_price']
            for item in line_items
        )
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Header
        story.append(Paragraph("INVOICE", self.styles['InvoiceTitle']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Company and client info
        info_data = [
            [self.company_name, "Invoice Number:", invoice_number],
            [self.company_address, "Invoice Date:", invoice_date.strftime('%B %d, %Y')],
            [self.company_email, "Due Date:", due_date.strftime('%B %d, %Y')],
            ["", "", ""],
            ["Bill To:", "", ""],
            [client_name, "", ""],
            [client_address, "", ""],
            [client_email, "", ""]
        ]
        
        info_table = Table(info_data, colWidths=[3 * inch, 1.5 * inch, 2 * inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 2), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 4), (0, 4), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (0, 5), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, 2), colors.HexColor('#1f4e79')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.5 * inch))
        
        # Line items
        table_data = [["Description", "Quantity", "Unit Price", "Amount"]]
        
        for item in line_items:
            amount = item['quantity'] * item['unit_price']
            table_data.append([
                item['description'],
                str(item['quantity']),
                f"{currency} {item['unit_price']:.2f}",
                f"{currency} {amount:.2f}"
            ])
        
        # Add totals
        table_data.append(["", "", "Subtotal:", f"{currency} {subtotal:.2f}"])
        
        if tax_rate > 0:
            table_data.append(["", "", f"Tax ({tax_rate * 100:.1f}%):", f"{currency} {tax_amount:.2f}"])
        
        table_data.append(["", "", "Total:", f"{currency} {total:.2f}"])
        
        items_table = Table(
            table_data,
            colWidths=[3.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch]
        )
        
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -4), colors.beige),
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            ('FONTNAME', (2, -3), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (2, -3), (-1, -3), 1, colors.black),
            ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black)
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 0.5 * inch))
        
        # Notes
        if notes:
            story.append(Paragraph("Notes:", self.styles['InvoiceHeading']))
            story.append(Paragraph(notes, self.styles['Normal']))
            story.append(Spacer(1, 0.3 * inch))
        
        # Payment info
        story.append(Paragraph(
            "Please make payment by the due date. Thank you for your business!",
            self.styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        
        # Save to database
        invoice_record = {
            "invoice_number": invoice_number,
            "client_name": client_name,
            "client_email": client_email,
            "total_amount": total,
            "currency": currency,
            "invoice_date": invoice_date.isoformat(),
            "due_date": due_date.isoformat(),
            "status": "pending",
            "output_file": str(output_file),
            "created_at": datetime.now().isoformat()
        }
        
        self.invoices.append(invoice_record)
        self._save_invoice_db()
        
        result = InvoiceResult(
            invoice_number=invoice_number,
            client_name=client_name,
            total_amount=total,
            currency=currency,
            status="pending",
            output_file=str(output_file),
            due_date=due_date.isoformat()
        )
        
        if self.verbose:
            print(f"✓ Invoice created: {invoice_number}")
            print(f"✓ Total: {currency} {total:.2f}")
            print(f"✓ Due: {due_date.strftime('%Y-%m-%d')}")
            print(f"✓ Saved to: {output_file}")
        
        return result
    
    def send_invoice(
        self,
        invoice_number: str,
        recipient_email: Optional[str] = None
    ) -> bool:
        """Send invoice via email.
        
        Note: This is a placeholder. Integrate with EmailCampaigner for actual sending.
        
        Args:
            invoice_number: Invoice number to send
            recipient_email: Recipient email (uses client email if None)
            
        Returns:
            True if successful
        """
        invoice = next(
            (inv for inv in self.invoices if inv['invoice_number'] == invoice_number),
            None
        )
        
        if not invoice:
            raise ValueError(f"Invoice not found: {invoice_number}")
        
        recipient = recipient_email or invoice['client_email']
        
        if self.verbose:
            print(f"Sending invoice {invoice_number} to {recipient}")
            print("Note: Email sending requires EmailCampaigner integration")
        
        # Update status
        invoice['status'] = 'sent'
        invoice['sent_at'] = datetime.now().isoformat()
        self._save_invoice_db()
        
        if self.verbose:
            print(f"✓ Invoice marked as sent")
        
        return True
    
    def track_payment(
        self,
        invoice_number: str,
        payment_date: Optional[datetime] = None,
        payment_amount: Optional[float] = None
    ) -> bool:
        """Track payment for an invoice.
        
        Args:
            invoice_number: Invoice number
            payment_date: Payment date (defaults to today)
            payment_amount: Payment amount (defaults to invoice total)
            
        Returns:
            True if successful
        """
        invoice = next(
            (inv for inv in self.invoices if inv['invoice_number'] == invoice_number),
            None
        )
        
        if not invoice:
            raise ValueError(f"Invoice not found: {invoice_number}")
        
        payment_date = payment_date or datetime.now()
        payment_amount = payment_amount or invoice['total_amount']
        
        if self.verbose:
            print(f"Recording payment for {invoice_number}")
        
        # Update invoice
        invoice['status'] = 'paid'
        invoice['paid_at'] = payment_date.isoformat()
        invoice['paid_amount'] = payment_amount
        self._save_invoice_db()
        
        if self.verbose:
            print(f"✓ Payment recorded: {invoice['currency']} {payment_amount:.2f}")
            print(f"✓ Status: {invoice['status']}")
        
        return True
    
    def send_reminder(
        self,
        invoice_number: str,
        reminder_type: Literal["gentle", "urgent"] = "gentle"
    ) -> bool:
        """Send payment reminder for overdue invoice.
        
        Note: This is a placeholder. Integrate with EmailCampaigner for actual sending.
        
        Args:
            invoice_number: Invoice number
            reminder_type: Type of reminder (gentle or urgent)
            
        Returns:
            True if successful
        """
        invoice = next(
            (inv for inv in self.invoices if inv['invoice_number'] == invoice_number),
            None
        )
        
        if not invoice:
            raise ValueError(f"Invoice not found: {invoice_number}")
        
        if invoice['status'] == 'paid':
            if self.verbose:
                print(f"Invoice {invoice_number} is already paid. No reminder needed.")
            return True
        
        due_date = datetime.fromisoformat(invoice['due_date'])
        days_overdue = (datetime.now() - due_date).days
        
        if self.verbose:
            print(f"Sending {reminder_type} reminder for {invoice_number}")
            print(f"Days overdue: {days_overdue}")
            print("Note: Email sending requires EmailCampaigner integration")
        
        # Update reminder history
        if 'reminders' not in invoice:
            invoice['reminders'] = []
        
        invoice['reminders'].append({
            "type": reminder_type,
            "sent_at": datetime.now().isoformat(),
            "days_overdue": days_overdue
        })
        
        self._save_invoice_db()
        
        if self.verbose:
            print(f"✓ Reminder logged")
        
        return True
    
    def get_outstanding_invoices(self) -> List[Dict]:
        """Get all outstanding (unpaid) invoices.
        
        Returns:
            List of outstanding invoice dicts
        """
        outstanding = [
            inv for inv in self.invoices
            if inv['status'] != 'paid'
        ]
        
        if self.verbose:
            print(f"Outstanding invoices: {len(outstanding)}")
            total_outstanding = sum(inv['total_amount'] for inv in outstanding)
            if outstanding:
                currency = outstanding[0]['currency']
                print(f"Total outstanding: {currency} {total_outstanding:.2f}")
        
        return outstanding


def create_simple_invoice(
    client_name: str,
    line_items: List[Dict],
    output_dir: str = "output/invoices",
    **kwargs
) -> InvoiceResult:
    """Convenience function to create an invoice.
    
    Args:
        client_name: Client name
        line_items: Invoice line items
        output_dir: Output directory
        **kwargs: Additional arguments for Invoicer
        
    Returns:
        InvoiceResult
    """
    invoicer = Invoicer(output_dir=output_dir)
    return invoicer.create_invoice(
        client_name=client_name,
        client_address="",
        client_email="",
        line_items=line_items,
        **kwargs
    )
