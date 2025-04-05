# documents/importers/sharepoint_import.py

from projects.models import Project
from django.contrib.auth.models import User
from documents.models import Document, DocumentVersion
from django.utils.timezone import now
from guardian.shortcuts import assign_perm
import tempfile
import requests
from django.core.files import File
from .models import SharePointImportLog


"""
SharePoint Importer Module
--------------------------
Handles ingestion of SharePoint list/library exports into the Django system.
Designed for CSV, Excel, or Graph API data. Contains stubs for mapping,
document creation, ACL conversion, and Power BI detection.
--------------------------

This script does not directly pull data from SharePoint servers.
Export SharePoint list data (e.g., via CSV or Excel), and then the script ingests it.

How This Script Works
Assumptions:
You download or export a SharePoint list/library manually or via automation

From PowerShell, Excel, or Microsoft Graph API
Usually in CSV or Excel format
What happens when you run it:

python manage.py runscript sharepoint_import
# or call import_from_csv("/path/to/export.csv")

Internally, it:
Reads the exported CSV file
Normalizes the field names
Maps SharePoint fields (like “Document Name”, “Upload Date”) to Django model fields
Creates:
Project if needed
Document and DocumentVersion
Dummy User entries if usernames don’t exist yet
Placeholder for importing file blobs (via URL field or manual blob)
Assigns permissions per row (e.g., who can view/edit)
Flags rows likely used in Power BI
Calls a logging function (to be implemented) to track what was imported



Realistic Workflow For Full Extraction
Here’s what a comprehensive SharePoint-to-Django migration workflow looks like:

🔹 STEP 1: Export Structured Data
CSV/XLSX for each list

Download or script via PowerShell or Graph API

🔹 STEP 2: Export Files
Use PowerShell (Get-PnPFile) or Graph to download all files

Store with document_name and map to rows via file_url

🔹 STEP 3: Extract Permissions
Run scripts to dump access control per document/list

Flatten into columns like can_view, can_edit, etc.

🔹 STEP 4: Manually Capture:
Power Automate workflows

Saved views and filters

Approval flows or custom logic

BI dashboards linked to the data

Summary: What You Can and Can't Get Easily
Artifact			CSV Export	API / PowerShell	Manual
List metadata			✅		✅			❌
Files				❌		✅			✅
Version history			❌		✅			❌
Permissions			❌		✅			✅
Comments			❌		❌			✅
Workflows (Power Automate)	❌		⚠️ (CLI only)		✅
Power BI usage			❌		❌			✅
View config			❌		❌			✅



"""

# documents/importers/sharepoint_import.py

import csv
from pathlib import Path

def import_from_csv(file_path):
    """Main entry point: takes a SharePoint-exported CSV and ingests rows."""
    if not Path(file_path).exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                parsed = parse_row(row)
                mapped = map_fields(parsed)
                create_project_if_needed(mapped)
                create_document(mapped)
                create_document_version(mapped)
                assign_permissions_from_acl(mapped)
                detect_power_bi_usage(mapped)
                record_import_event(mapped, success=True)
            except Exception as e:
                record_import_event(row, success=False, errors=str(e))


def parse_row(row):
    """Normalize a single row of SharePoint data into structured dict."""
    # Normalize keys (e.g., remove whitespace, lower-case)
    normalized = {}
    for k, v in row.items():
        key = k.strip().lower().replace(' ', '_')
        normalized[key] = v.strip() if isinstance(v, str) else v
    return normalized



DEFAULT_FIELD_MAP = {
    'document_name': 'title',
    'description': 'notes',
    'project_name': 'project',
    'uploaded_by': 'uploaded_by',
    'upload_date': 'uploaded_at',
    'file_url': 'file_url',
    'version': 'version',
    'tags': 'tags',
    'powerbi_flag': 'powerbi'
}


def map_fields(parsed_row):
    """Map SharePoint field names to Django model field names."""
    mapped = {}
    for sp_field, django_field in DEFAULT_FIELD_MAP.items():
        value = parsed_row.get(sp_field)
        if value:
            mapped[django_field] = value
    return mapped


def create_project_if_needed(mapped_fields):
    """Create or retrieve a Project based on metadata in the row."""
    name = mapped_fields.get('project')
    if not name:
        raise ValueError("Missing project field in mapped data.")

    project, _ = Project.objects.get_or_create(name=name)
    mapped_fields['project_obj'] = project


def create_document(mapped_fields):
    """Create Document record if one does not already exist."""
    title = mapped_fields.get('title')
    project = mapped_fields.get('project_obj')
    if not title or not project:
        raise ValueError("Missing document title or project.")

    doc, created = Document.objects.get_or_create(
        project=project,
        title=title,
        defaults={
            'description': mapped_fields.get('notes', ''),
            'created_by': get_or_stub_user(mapped_fields.get('uploaded_by')),
        }
    )
    mapped_fields['document_obj'] = doc


def create_document_version(mapped_fields, file_blob=None):
    """Attach a versioned file to the document. Optionally pass a file handle."""
    doc = mapped_fields.get('document_obj')
    if not doc:
        raise ValueError("Missing document reference for versioning.")

    version_number = int(mapped_fields.get('version', 1))
    file_url = mapped_fields.get('file_url')
    file_blob = download_file(file_url) if file_url else None

    DocumentVersion.objects.create(
        document=doc,
        version_number=version_number,
        file=file_blob if file_blob else "mock/path/or/blob",  # Replace when integrating real upload
        notes=mapped_fields.get('notes', ''),
        uploaded_by=get_or_stub_user(mapped_fields.get('uploaded_by')),
        uploaded_at=parsed_or_now(mapped_fields.get('uploaded_at'))
    )

def get_or_stub_user(username):
    """Get a User by username or create a placeholder if missing."""
    if not username:
        return User.objects.get_or_create(username='unknown-import')[0]
    return User.objects.get_or_create(username=username)[0]


def parsed_or_now(dt_string):
    """Try to parse datetime string or return now()."""
    from dateutil import parser
    try:
        return parser.parse(dt_string)
    except Exception:
        return now()

def assign_permissions_from_acl(mapped_fields):
    """Convert SharePoint role/user/group mappings into django-guardian permissions."""
    doc = mapped_fields.get('document_obj')
    if not doc:
        raise ValueError("Cannot assign permissions without document.")

    acl_map = {
        'can_view': 'commenter',   # lowest access
        'can_edit': 'editor',
        'is_owner': 'owner'
    }

    for acl_field, role in acl_map.items():
        raw = mapped_fields.get(acl_field)
        if not raw:
            continue

        usernames = [u.strip() for u in raw.split(',') if u.strip()]
        for username in usernames:
            user = get_or_stub_user(username)
            assign_perm(f'documents.{role}_document', user, doc)


def detect_power_bi_usage(mapped_fields):
    """Check for evidence that this list/library is used by Power BI (tags, usage notes)."""
    tags = mapped_fields.get('tags', '').lower()
    notes = mapped_fields.get('notes', '').lower()
    powerbi_flag = mapped_fields.get('powerbi', '').lower()

    indicators = ['bi', 'dashboard', 'powerbi', 'kpi']
    found = any(ind in tags or ind in notes or ind in powerbi_flag for ind in indicators)

    if found:
        mapped_fields['powerbi_detected'] = True


def record_import_event(mapped_fields, success=True, errors=None):
    """Store a log of the import event, outcome, and metadata for traceability."""
    SharePointImportLog.objects.create(
        title=mapped_fields.get('title'),
        project=mapped_fields.get('project_obj'),
        user=get_or_stub_user(mapped_fields.get('uploaded_by')),
        success=success,
        error_detail=errors or "",
        detected_powerbi=mapped_fields.get('powerbi_detected', False),
        source_site=mapped_fields.get('source_site', ''),
        source_list=mapped_fields.get('source_list', ''),
        raw_row=mapped_fields  # Preserve everything
    )

DOWNLOAD_ENABLED = True  # Toggle this off for dry run

def download_file(url):
    """Download a file from SharePoint or external storage."""
    if not DOWNLOAD_ENABLED:
        return None

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        temp = tempfile.NamedTemporaryFile(delete=False)
        for chunk in response.iter_content(1024 * 1024):
            temp.write(chunk)
        temp.seek(0)
        return File(temp, name=Path(url).name)
    except Exception as e:
        print(f"Download failed: {e}")
        return None
