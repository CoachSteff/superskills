"""
CLI command: migrate - Export/import profiles and settings
"""
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from cli.utils.paths import get_project_root, get_user_config_dir
from cli.utils.migration import (
    collect_skill_profiles,
    collect_skill_configs,
    calculate_checksum,
    validate_manifest,
    create_backup,
    merge_env_files,
    parse_env_file,
    write_env_file
)


def _get_version() -> str:
    """Read version from pyproject.toml."""
    pyproject_path = get_project_root() / "pyproject.toml"
    try:
        with open(pyproject_path, 'r') as f:
            for line in f:
                if line.strip().startswith('version'):
                    version = line.split('=')[1].strip().strip('"').strip("'")
                    return version
    except Exception:
        pass
    return "unknown"


def migrate_command(migrate_action: str, output: str = None, input: str = None,
                   include_api_keys: bool = False, dry_run: bool = False,
                   yes: bool = False, overwrite: bool = False, merge: bool = False):
    """
    Export or import profiles and settings.
    
    Args:
        migrate_action: 'export' or 'import'
        output: Output file path for export
        input: Input file path for import
        include_api_keys: Include API keys in export
        dry_run: Preview import changes without applying
        yes: Skip confirmation prompts
        overwrite: Overwrite all existing files on import
        merge: Merge configurations on import
    """
    if migrate_action == 'export':
        return _export_migration(output, include_api_keys)
    elif migrate_action == 'import':
        if not input:
            print("Error: Input file is required for import")
            return 1
        return _import_migration(input, dry_run, yes, overwrite, merge)
    else:
        print(f"Error: Unknown migrate action: {migrate_action}")
        return 1


def _export_migration(output_path: str = None, include_api_keys: bool = False) -> int:
    """
    Export migration package.
    
    Args:
        output_path: Optional output file path
        include_api_keys: Include API keys in export
        
    Returns:
        Exit code
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if not output_path:
        output_path = f"superskills-migration-{timestamp}.zip"
    
    output_file = Path(output_path)
    
    print("Creating migration package...")
    
    if include_api_keys:
        print("\n⚠️  WARNING: API keys will be included in this export!")
        print("   Keep this file secure and delete it after transfer.\n")
    
    # Collect all files
    user_config_dir = get_user_config_dir()
    project_root = get_project_root()
    
    files_to_export = {}
    
    # User config files
    config_yaml = user_config_dir / "config.yaml"
    if config_yaml.exists():
        files_to_export["user-config/config.yaml"] = config_yaml
    
    master_briefing = user_config_dir / "master-briefing.yaml"
    if master_briefing.exists():
        files_to_export["user-config/master-briefing.yaml"] = master_briefing
    
    # API keys (optional)
    if include_api_keys:
        env_file = project_root / ".env"
        if env_file.exists():
            files_to_export["env/.env"] = env_file
    
    # Skill profiles
    profiles = collect_skill_profiles()
    for skill_name, profile_path in profiles:
        files_to_export[f"skill-profiles/{skill_name}/PROFILE.md"] = profile_path
    
    # Skill configs
    configs = collect_skill_configs()
    for relative_path, config_path in configs:
        files_to_export[f"skill-configs/{relative_path}"] = config_path
    
    # Generate manifest
    manifest = {
        "version": _get_version(),
        "export_timestamp": timestamp,
        "flags": {
            "api_keys_included": include_api_keys,
            "profiles_included": len(profiles) > 0,
            "configs_included": len(configs) > 0
        },
        "files": {}
    }
    
    # Create ZIP archive
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for archive_path, file_path in files_to_export.items():
                zipf.write(file_path, archive_path)
                manifest["files"][archive_path] = {
                    "checksum": calculate_checksum(file_path),
                    "size": file_path.stat().st_size
                }
            
            # Write manifest
            manifest_json = json.dumps(manifest, indent=2)
            zipf.writestr("manifest.json", manifest_json)
        
        # Display summary
        print("\n✅ Migration package created successfully!")
        print(f"\nLocation: {output_file.absolute()}")
        print(f"Size: {output_file.stat().st_size:,} bytes")
        print(f"\nContents:")
        print(f"  • Config files: {1 if config_yaml.exists() else 0}")
        print(f"  • Master Briefing: {1 if master_briefing.exists() else 0}")
        print(f"  • Skill profiles: {len(profiles)}")
        print(f"  • Skill configs: {len(configs)}")
        print(f"  • API keys: {'Yes' if include_api_keys else 'No'}")
        
        if include_api_keys:
            print("\n⚠️  Remember to keep this file secure and delete after transfer!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error creating migration package: {e}")
        return 1


def _import_migration(input_path: str, dry_run: bool = False, 
                     skip_confirm: bool = False, overwrite: bool = False,
                     merge: bool = False) -> int:
    """
    Import migration package.
    
    Args:
        input_path: Path to migration ZIP file
        dry_run: Preview changes without applying
        skip_confirm: Skip confirmation prompts
        overwrite: Overwrite all existing files
        merge: Merge configurations
        
    Returns:
        Exit code
    """
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"❌ Error: Migration file not found: {input_file}")
        return 1
    
    if not zipfile.is_zipfile(input_file):
        print(f"❌ Error: Invalid ZIP file: {input_file}")
        return 1
    
    print(f"Reading migration package: {input_file.name}")
    
    try:
        with zipfile.ZipFile(input_file, 'r') as zipf:
            # Read and validate manifest
            try:
                manifest_data = zipf.read("manifest.json")
                manifest = json.loads(manifest_data)
            except KeyError:
                print("❌ Error: Invalid migration package (missing manifest)")
                return 1
            
            if not validate_manifest(manifest):
                print("❌ Error: Invalid manifest structure")
                return 1
            
            # Display package info
            print(f"\nPackage Information:")
            print(f"  Version: {manifest['version']}")
            print(f"  Exported: {manifest['export_timestamp']}")
            print(f"\nContents:")
            
            file_count = {
                'config': 0,
                'master_briefing': 0,
                'profiles': 0,
                'configs': 0,
                'env': 0
            }
            
            for archive_path in manifest['files'].keys():
                if archive_path.startswith('user-config/config.yaml'):
                    file_count['config'] += 1
                elif archive_path.startswith('user-config/master-briefing.yaml'):
                    file_count['master_briefing'] += 1
                elif archive_path.startswith('skill-profiles/'):
                    file_count['profiles'] += 1
                elif archive_path.startswith('skill-configs/'):
                    file_count['configs'] += 1
                elif archive_path.startswith('env/'):
                    file_count['env'] += 1
            
            print(f"  • Config files: {file_count['config']}")
            print(f"  • Master Briefing: {file_count['master_briefing']}")
            print(f"  • Skill profiles: {file_count['profiles']}")
            print(f"  • Skill configs: {file_count['configs']}")
            print(f"  • API keys: {file_count['env']}")
            
            if file_count['env'] > 0:
                print("\n⚠️  WARNING: This package contains API keys!")
            
            # Check version compatibility
            current_version = _get_version()
            if manifest['version'] != current_version:
                print(f"\n⚠️  Version mismatch: Package={manifest['version']}, Current={current_version}")
            
            if dry_run:
                print("\n📋 Dry-run mode: No changes will be made")
                _preview_import(zipf, manifest)
                return 0
            
            # Confirm import
            if not skip_confirm:
                response = input("\nProceed with import? [y/N]: ")
                if response.lower() != 'y':
                    print("Import cancelled")
                    return 0
            
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = get_user_config_dir() / "backups" / f"backup-{timestamp}"
            
            print(f"\nCreating backup: {backup_dir}")
            files_to_backup = _collect_files_to_backup(manifest)
            create_backup(files_to_backup, backup_dir)
            
            # Extract and apply files
            print("\nImporting files...")
            _apply_import(zipf, manifest, overwrite, merge)
            
            print("\n✅ Migration imported successfully!")
            print(f"\nBackup location: {backup_dir}")
            print("\nTo rollback, restore files from the backup directory.")
            
            return 0
            
    except Exception as e:
        print(f"\n❌ Error importing migration: {e}")
        import traceback
        traceback.print_exc()
        return 1


def _preview_import(zipf: zipfile.ZipFile, manifest: Dict[str, Any]) -> None:
    """Preview what will be imported."""
    print("\nFiles that will be imported:")
    
    for archive_path, file_info in manifest['files'].items():
        target_path = _get_target_path(archive_path)
        exists = target_path.exists() if target_path else False
        status = "overwrite" if exists else "new"
        print(f"  [{status:9}] {archive_path} → {target_path}")


def _collect_files_to_backup(manifest: Dict[str, Any]) -> list:
    """Collect files that need backup before import."""
    files_to_backup = []
    
    for archive_path in manifest['files'].keys():
        target_path = _get_target_path(archive_path)
        if target_path and target_path.exists():
            files_to_backup.append(target_path)
    
    return files_to_backup


def _get_target_path(archive_path: str) -> Path:
    """
    Get target path for an archive path.
    
    Args:
        archive_path: Path within ZIP archive
        
    Returns:
        Target path on filesystem
    """
    user_config_dir = get_user_config_dir()
    project_root = get_project_root()
    
    if archive_path.startswith('user-config/'):
        relative = archive_path.replace('user-config/', '', 1)
        return user_config_dir / relative
    elif archive_path.startswith('env/'):
        relative = archive_path.replace('env/', '', 1)
        return project_root / relative
    elif archive_path.startswith('skill-profiles/'):
        relative = archive_path.replace('skill-profiles/', '', 1)
        return project_root / "superskills" / relative
    elif archive_path.startswith('skill-configs/'):
        relative = archive_path.replace('skill-configs/', '', 1)
        return project_root / "superskills" / relative
    
    return None


def _apply_import(zipf: zipfile.ZipFile, manifest: Dict[str, Any],
                 overwrite: bool = False, merge: bool = False) -> None:
    """
    Apply imported files to filesystem.
    
    Args:
        zipf: Open ZIP file
        manifest: Manifest data
        overwrite: Overwrite existing files
        merge: Merge configurations
    """
    project_root = get_project_root()
    
    for archive_path, file_info in manifest['files'].items():
        target_path = _get_target_path(archive_path)
        
        if not target_path:
            continue
        
        # Special handling for .env files (merge)
        if archive_path.startswith('env/.env'):
            _import_env_file(zipf, archive_path, target_path, merge)
            continue
        
        # Check if file exists and handle conflicts
        if target_path.exists() and not overwrite:
            if not merge:
                print(f"  ⏭️  Skipping (exists): {archive_path}")
                continue
        
        # Extract file
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        with zipf.open(archive_path) as source:
            with open(target_path, 'wb') as target:
                target.write(source.read())
        
        # Verify checksum
        actual_checksum = calculate_checksum(target_path)
        expected_checksum = file_info['checksum']
        
        if actual_checksum != expected_checksum:
            print(f"  ⚠️  Checksum mismatch: {archive_path}")
        else:
            print(f"  ✅ Imported: {archive_path}")


def _import_env_file(zipf: zipfile.ZipFile, archive_path: str, 
                    target_path: Path, merge: bool = True) -> None:
    """
    Import .env file with merge strategy.
    
    Args:
        zipf: Open ZIP file
        archive_path: Path in archive
        target_path: Target file path
        merge: Use merge strategy
    """
    # Read new env vars
    with zipf.open(archive_path) as f:
        new_env_content = f.read().decode('utf-8')
    
    # Parse new env vars
    new_env = {}
    for line in new_env_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, value = line.split('=', 1)
            new_env[key.strip()] = value.strip().strip('"').strip("'")
    
    if merge and target_path.exists():
        # Merge with existing
        existing_env = parse_env_file(target_path)
        merged_env = merge_env_files(existing_env, new_env)
        
        write_env_file(target_path, merged_env)
        print(f"  ✅ Merged API keys: {archive_path}")
        
        # Show what was added
        added_keys = set(new_env.keys()) - set(existing_env.keys())
        if added_keys:
            print(f"     Added keys: {', '.join(added_keys)}")
    else:
        # Overwrite
        write_env_file(target_path, new_env)
        print(f"  ✅ Imported API keys: {archive_path}")
