import subprocess
import sys
from pathlib import Path
from typing import List, Set

def read_requirements(requirements_file: str = "requirements.txt"):
    """
    Read existing requirements from requirements.txt file.
    
    Args:
        requirements_file: Path to requirements.txt file
        
    Returns:
        Set of package names from requirements.txt
    """
    requirements_path = Path(requirements_file)
    existing_packages = set()
    
    if requirements_path.exists():
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        # Extract package name (ignore version specifiers)
                        package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('~=')[0].strip()
                        existing_packages.add(package_name.lower())
        except IOError as e:
            print(f"Error reading {requirements_file}: {e}")
    else:
        print(f"{requirements_file} not found. Will create new file.")
    
    return existing_packages

def find_missing_dependencies(dependency_list: List[str], requirements_file: str = "requirements.txt") -> List[str]:
    """
    Find dependencies that are missing from requirements.txt file.
    
    Args:
        dependency_list: List of required dependencies
        requirements_file: Path to requirements.txt file
        
    Returns:
        List of missing dependencies
    """
    existing_packages = read_requirements(requirements_file)
    missing_packages = []
    
    for dependency in dependency_list:
        # Normalize package name for comparison
        package_name = dependency.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('~=')[0].strip().lower()
        if package_name not in existing_packages:
            missing_packages.append(dependency)
    
    return missing_packages

def append_to_requirements(missing_dependencies: List[str], requirements_file: str = "requirements.txt") -> bool:
    """
    Append missing dependencies to requirements.txt file.
    
    Args:
        missing_dependencies: List of dependencies to append
        requirements_file: Path to requirements.txt file
        
    Returns:
        True if successful, False otherwise
    """
    if not missing_dependencies:
        print("No missing dependencies to append.")
        return True
    
    try:
        # Create file if it doesn't exist, or append if it does
        with open(requirements_file, 'a', encoding='utf-8') as f:
            # Add newline if file exists and doesn't end with newline
            requirements_path = Path(requirements_file)
            if requirements_path.exists() and requirements_path.stat().st_size > 0:
                # Check if last character is newline
                with open(requirements_file, 'rb') as check_file:
                    check_file.seek(-1, 2)  # Go to last character
                    if check_file.read(1) != b'\n':
                        f.write('\n')
            
            # Append missing dependencies
            for dependency in missing_dependencies:
                f.write(f"{dependency}\n")
                
        print(f"Successfully appended {len(missing_dependencies)} dependencies to {requirements_file}")
        print("Appended packages:", ", ".join(missing_dependencies))
        return True
        
    except IOError as e:
        print(f"Error writing to {requirements_file}: {e}")
        return False

def install_packages(packages: List[str], use_pip_upgrade: bool = False) -> bool:
    """
    Install packages using pip via subprocess.
    
    Args:
        packages: List of package names to install
        use_pip_upgrade: Whether to use --upgrade flag
        
    Returns:
        True if installation successful, False otherwise
    """
    if not packages:
        print("No packages to install.")
        return True
    
    try:
        cmd = [sys.executable, "-m", "pip", "install"]
        
        if use_pip_upgrade:
            cmd.append("--upgrade")
            
        cmd.extend(packages)
        
        print(f"Installing packages: {', '.join(packages)}")
        print(f"Running command: {' '.join(cmd)}")
        
        # Run pip install command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("Installation successful!")
        if result.stdout:
            print("STDOUT:", result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Installation failed with return code {e.returncode}")
        print("STDERR:", e.stderr)
        if e.stdout:
            print("STDOUT:", e.stdout)
        return False
    except Exception as e:
        print(f"Unexpected error during installation: {e}")
        return False

def manage_dependencies(dependency_list: List[str], requirements_file: str = "requirements.txt", 
                       install_missing: bool = True, use_pip_upgrade: bool = False) -> bool:
    """
    Main function to manage dependencies - check, append, and install missing packages.
    
    Args:
        dependency_list: List of required dependencies
        requirements_file: Path to requirements.txt file
        install_missing: Whether to install missing packages
        use_pip_upgrade: Whether to use --upgrade flag when installing
        
    Returns:
        True if all operations successful, False otherwise
    """
    print(f"Checking dependencies against {requirements_file}...")
    
    # Find missing dependencies
    missing_deps = find_missing_dependencies(dependency_list, requirements_file)
    
    if not missing_deps:
        print("All dependencies are already in requirements.txt")
        return True
    
    print(f"Found {len(missing_deps)} missing dependencies: {', '.join(missing_deps)}")
    
    # Append missing dependencies to requirements.txt
    if not append_to_requirements(missing_deps, requirements_file):
        return False
    
    # Install missing packages if requested
    if install_missing:
        return install_packages(missing_deps, use_pip_upgrade)
    
    return True

# Example usage
if __name__ == "__main__":
    # Example dependency list
    required_dependencies = [
        "requests>=2.28.0",
        "numpy==1.24.3",
        "pandas>=1.5.0",
        "flask==2.3.2",
        "python-dotenv"
    ]
    
    # Manage dependencies
    success = manage_dependencies(
        dependency_list=required_dependencies,
        requirements_file="requirements.txt",
        install_missing=True,
        use_pip_upgrade=False
    )
    
    if success:
        print("\nDependency management completed successfully!")
    else:
        print("\nDependency management failed!")
        sys.exit(1)