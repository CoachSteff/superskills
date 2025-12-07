"""
CoursePackager.py - Course packaging and workbook generation.
"""
import os
from typing import Dict, List, Optional, Literal
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import zipfile
import json

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not available - install with: pip install reportlab")


@dataclass
class CoursePackageResult:
    """Result from a course packaging operation."""
    package_name: str
    output_file: str
    package_type: str
    file_count: int
    file_size_mb: float
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class CoursePackager:
    """Course packaging and workbook generation using reportlab."""
    
    def __init__(
        self,
        output_dir: str = "output/courses",
        verbose: bool = True
    ):
        """Initialize CoursePackager.
        
        Args:
            output_dir: Directory to save course packages
            verbose: Enable verbose logging
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required. Install with: pip install reportlab")
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom PDF styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4e79'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2e75b6'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_LEFT
        ))
    
    def create_workbook(
        self,
        title: str,
        sections: List[Dict[str, any]],
        output_name: Optional[str] = None,
        include_toc: bool = True
    ) -> CoursePackageResult:
        """Create a course workbook PDF.
        
        Args:
            title: Workbook title
            sections: List of section dicts with 'title', 'content', 'exercises'
            output_name: Output filename (without extension)
            include_toc: Include table of contents
            
        Returns:
            CoursePackageResult with workbook details
        """
        if self.verbose:
            print(f"Creating workbook: {title}")
        
        output_file = self.output_dir / (output_name or f"{title.replace(' ', '_')}.pdf")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        
        # Title page
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y')}",
            self.styles['Normal']
        ))
        story.append(PageBreak())
        
        # Table of contents
        if include_toc:
            story.append(Paragraph("Table of Contents", self.styles['CustomTitle']))
            story.append(Spacer(1, 0.3 * inch))
            
            for i, section in enumerate(sections, 1):
                toc_entry = f"{i}. {section['title']}"
                story.append(Paragraph(toc_entry, self.styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))
            
            story.append(PageBreak())
        
        # Add sections
        for i, section in enumerate(sections, 1):
            # Section title
            story.append(Paragraph(
                f"Section {i}: {section['title']}",
                self.styles['CustomTitle']
            ))
            story.append(Spacer(1, 0.3 * inch))
            
            # Section content
            if 'content' in section:
                for paragraph in section['content']:
                    story.append(Paragraph(paragraph, self.styles['CustomBody']))
                    story.append(Spacer(1, 0.1 * inch))
            
            # Exercises
            if 'exercises' in section:
                story.append(Spacer(1, 0.3 * inch))
                story.append(Paragraph("Exercises", self.styles['CustomHeading']))
                
                for j, exercise in enumerate(section['exercises'], 1):
                    story.append(Paragraph(
                        f"{j}. {exercise}",
                        self.styles['CustomBody']
                    ))
                    story.append(Spacer(1, 0.5 * inch))
            
            story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        
        result = CoursePackageResult(
            package_name=title,
            output_file=str(output_file),
            package_type="workbook",
            file_count=1,
            file_size_mb=file_size_mb
        )
        
        if self.verbose:
            print(f"✓ Workbook created: {len(sections)} sections")
            print(f"✓ Saved to: {output_file}")
        
        return result
    
    def generate_certificate(
        self,
        student_name: str,
        course_name: str,
        completion_date: Optional[datetime] = None,
        instructor_name: Optional[str] = None,
        output_name: Optional[str] = None
    ) -> CoursePackageResult:
        """Generate a course completion certificate.
        
        Args:
            student_name: Student's name
            course_name: Course name
            completion_date: Completion date (defaults to today)
            instructor_name: Instructor's name
            output_name: Output filename
            
        Returns:
            CoursePackageResult with certificate details
        """
        if self.verbose:
            print(f"Generating certificate for: {student_name}")
        
        completion_date = completion_date or datetime.now()
        output_file = self.output_dir / (output_name or f"certificate_{student_name.replace(' ', '_')}.pdf")
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=letter
        )
        
        story = []
        
        # Certificate border/header
        story.append(Spacer(1, 1.5 * inch))
        
        # Title
        story.append(Paragraph(
            "Certificate of Completion",
            self.styles['CustomTitle']
        ))
        story.append(Spacer(1, 0.5 * inch))
        
        # Recipient
        story.append(Paragraph(
            "This is to certify that",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.2 * inch))
        
        story.append(Paragraph(
            student_name,
            self.styles['CustomTitle']
        ))
        story.append(Spacer(1, 0.3 * inch))
        
        # Course info
        story.append(Paragraph(
            "has successfully completed",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.2 * inch))
        
        story.append(Paragraph(
            course_name,
            self.styles['CustomHeading']
        ))
        story.append(Spacer(1, 0.5 * inch))
        
        # Date
        story.append(Paragraph(
            f"Completion Date: {completion_date.strftime('%B %d, %Y')}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 1 * inch))
        
        # Instructor signature
        if instructor_name:
            story.append(Paragraph(
                f"_________________________",
                self.styles['Normal']
            ))
            story.append(Paragraph(
                instructor_name,
                self.styles['Normal']
            ))
            story.append(Paragraph(
                "Instructor",
                self.styles['Normal']
            ))
        
        doc.build(story)
        
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        
        result = CoursePackageResult(
            package_name=f"Certificate - {student_name}",
            output_file=str(output_file),
            package_type="certificate",
            file_count=1,
            file_size_mb=file_size_mb
        )
        
        if self.verbose:
            print(f"✓ Certificate generated")
            print(f"✓ Saved to: {output_file}")
        
        return result
    
    def bundle_resources(
        self,
        resource_paths: List[str],
        bundle_name: str,
        include_manifest: bool = True
    ) -> CoursePackageResult:
        """Bundle course resources into a ZIP file.
        
        Args:
            resource_paths: List of file/directory paths to include
            bundle_name: Name of the bundle
            include_manifest: Include a manifest file
            
        Returns:
            CoursePackageResult with bundle details
        """
        if self.verbose:
            print(f"Bundling {len(resource_paths)} resources...")
        
        output_file = self.output_dir / f"{bundle_name}.zip"
        
        # Create ZIP file
        file_count = 0
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            manifest = []
            
            for resource_path in resource_paths:
                resource = Path(resource_path)
                
                if resource.is_file():
                    zipf.write(resource, resource.name)
                    file_count += 1
                    manifest.append({
                        "name": resource.name,
                        "type": "file",
                        "size": resource.stat().st_size
                    })
                    
                elif resource.is_dir():
                    for file_path in resource.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(resource.parent)
                            zipf.write(file_path, arcname)
                            file_count += 1
                            manifest.append({
                                "name": str(arcname),
                                "type": "file",
                                "size": file_path.stat().st_size
                            })
            
            # Add manifest
            if include_manifest:
                manifest_data = {
                    "bundle_name": bundle_name,
                    "created_at": datetime.now().isoformat(),
                    "file_count": file_count,
                    "files": manifest
                }
                
                zipf.writestr(
                    "manifest.json",
                    json.dumps(manifest_data, indent=2)
                )
                file_count += 1
        
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        
        result = CoursePackageResult(
            package_name=bundle_name,
            output_file=str(output_file),
            package_type="bundle",
            file_count=file_count,
            file_size_mb=file_size_mb
        )
        
        if self.verbose:
            print(f"✓ Bundle created: {file_count} files")
            print(f"✓ Saved to: {output_file}")
        
        return result
    
    def create_course_package(
        self,
        course_name: str,
        workbook_sections: List[Dict],
        resource_paths: Optional[List[str]] = None,
        include_certificate_template: bool = True
    ) -> CoursePackageResult:
        """Create a complete course package.
        
        Args:
            course_name: Course name
            workbook_sections: Workbook sections
            resource_paths: Additional resource files to include
            include_certificate_template: Include blank certificate template
            
        Returns:
            CoursePackageResult with complete package
        """
        if self.verbose:
            print(f"Creating complete course package: {course_name}")
        
        package_dir = self.output_dir / course_name.replace(' ', '_')
        package_dir.mkdir(parents=True, exist_ok=True)
        
        files_created = []
        
        # Create workbook
        workbook_result = self.create_workbook(
            title=f"{course_name} - Workbook",
            sections=workbook_sections,
            output_name=str(package_dir / "workbook.pdf")
        )
        files_created.append(workbook_result.output_file)
        
        # Create certificate template
        if include_certificate_template:
            cert_result = self.generate_certificate(
                student_name="[Student Name]",
                course_name=course_name,
                instructor_name="[Instructor Name]",
                output_name=str(package_dir / "certificate_template.pdf")
            )
            files_created.append(cert_result.output_file)
        
        # Copy additional resources
        if resource_paths:
            resources_dir = package_dir / "resources"
            resources_dir.mkdir(exist_ok=True)
            
            for resource_path in resource_paths:
                resource = Path(resource_path)
                if resource.exists():
                    import shutil
                    if resource.is_file():
                        dest = resources_dir / resource.name
                        shutil.copy2(resource, dest)
                        files_created.append(str(dest))
        
        # Bundle everything into ZIP
        bundle_result = self.bundle_resources(
            resource_paths=[str(package_dir)],
            bundle_name=f"{course_name}_package",
            include_manifest=True
        )
        
        if self.verbose:
            print(f"✓ Complete package created: {len(files_created)} files")
            print(f"✓ Package saved to: {bundle_result.output_file}")
        
        return bundle_result


def create_course_workbook(
    title: str,
    sections: List[Dict],
    output_dir: str = "output/courses",
    **kwargs
) -> CoursePackageResult:
    """Convenience function to create a course workbook.
    
    Args:
        title: Workbook title
        sections: Workbook sections
        output_dir: Output directory
        **kwargs: Additional arguments for CoursePackager
        
    Returns:
        CoursePackageResult
    """
    packager = CoursePackager(output_dir=output_dir)
    return packager.create_workbook(title, sections, **kwargs)
