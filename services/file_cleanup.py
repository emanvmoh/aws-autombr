import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class FileCleanup:
    """Handle cleanup of temporary files and old outputs."""
    
    @staticmethod
    def cleanup_file(filepath: str) -> bool:
        """
        Delete a single file.
        
        Args:
            filepath: Path to file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Deleted: {filepath}")
                return True
            return False
        except Exception as e:
            print(f"Error deleting {filepath}: {e}")
            return False
    
    @staticmethod
    def cleanup_directory(directory: str, max_age_hours: int = 24) -> int:
        """
        Delete files older than max_age_hours from a directory.
        
        Args:
            directory: Directory path to clean
            max_age_hours: Maximum age of files to keep (in hours)
            
        Returns:
            Number of files deleted
        """
        if not os.path.exists(directory):
            return 0
        
        deleted_count = 0
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        try:
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                
                if os.path.isfile(filepath):
                    file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if file_modified < cutoff_time:
                        if FileCleanup.cleanup_file(filepath):
                            deleted_count += 1
        except Exception as e:
            print(f"Error cleaning directory {directory}: {e}")
        
        return deleted_count
    
    @staticmethod
    def cleanup_session_files(session_id: str, upload_folder: str, output_folder: str) -> bool:
        """
        Delete all files associated with a session.
        
        Args:
            session_id: Session identifier
            upload_folder: Path to uploads directory
            output_folder: Path to outputs directory
            
        Returns:
            True if all files deleted successfully
        """
        success = True
        
        # Clean uploads
        for filename in os.listdir(upload_folder):
            if session_id in filename:
                filepath = os.path.join(upload_folder, filename)
                if not FileCleanup.cleanup_file(filepath):
                    success = False
        
        # Clean outputs
        for filename in os.listdir(output_folder):
            if session_id in filename:
                filepath = os.path.join(output_folder, filename)
                if not FileCleanup.cleanup_file(filepath):
                    success = False
        
        return success
    
    @staticmethod
    def cleanup_old_files(upload_folder: str, output_folder: str, max_age_hours: int = 24):
        """
        Clean old files from both upload and output directories.
        
        Args:
            upload_folder: Path to uploads directory
            output_folder: Path to outputs directory
            max_age_hours: Maximum age of files to keep
        """
        print(f"\nCleaning files older than {max_age_hours} hours...")
        
        uploads_deleted = FileCleanup.cleanup_directory(upload_folder, max_age_hours)
        outputs_deleted = FileCleanup.cleanup_directory(output_folder, max_age_hours)
        
        total = uploads_deleted + outputs_deleted
        print(f"Cleanup complete: {total} files deleted ({uploads_deleted} uploads, {outputs_deleted} outputs)")
