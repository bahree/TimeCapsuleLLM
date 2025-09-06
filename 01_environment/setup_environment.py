#!/usr/bin/env python3
"""
Environment Setup for London Historical LLM
Sets up Python environment, installs dependencies, and configures paths
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import json

class EnvironmentSetup:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).resolve()
        self.system = platform.system().lower()
        self.python_version = sys.version_info
        
        # Environment configuration
        self.config = {
            'python_version': f"{self.python_version.major}.{self.python_version.minor}",
            'system': self.system,
            'project_root': str(self.project_root),
            'data_dir': str(self.project_root / "data"),
            'models_dir': str(self.project_root / "09_models"),
            'logs_dir': str(self.project_root / "logs"),
            'venv_name': "london-llm-env"
        }
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🐍 Checking Python version...")
        
        if self.python_version < (3, 8):
            print(f"❌ Python {self.python_version.major}.{self.python_version.minor} is not supported")
            print("   Minimum required: Python 3.8")
            return False
        
        print(f"✅ Python {self.python_version.major}.{self.python_version.minor} is compatible")
        return True
    
    def check_system_requirements(self):
        """Check system requirements"""
        print("\n💻 Checking system requirements...")
        
        # Check available memory
        try:
            if self.system == "windows":
                import psutil
                memory_gb = psutil.virtual_memory().total / (1024**3)
            else:
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                memory_gb = int(meminfo.split('\n')[0].split()[1]) / (1024**2)
            
            print(f"   RAM: {memory_gb:.1f} GB")
            if memory_gb < 8:
                print("   ⚠️  Warning: Less than 8GB RAM detected")
            else:
                print("   ✅ Sufficient RAM")
                
        except Exception as e:
            print(f"   ⚠️  Could not check RAM: {e}")
        
        # Check disk space
        try:
            if self.system == "windows":
                import shutil
                free_space = shutil.disk_usage(self.project_root).free / (1024**3)
            else:
                statvfs = os.statvfs(self.project_root)
                free_space = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)
            
            print(f"   Disk space: {free_space:.1f} GB available")
            if free_space < 10:
                print("   ⚠️  Warning: Less than 10GB free space")
            else:
                print("   ✅ Sufficient disk space")
                
        except Exception as e:
            print(f"   ⚠️  Could not check disk space: {e}")
        
        return True
    
    def create_directories(self):
        """Create necessary directories"""
        print("\n📁 Creating project directories...")
        
        directories = [
            "data",
            "data/london_historical",
            "09_models",
            "09_models/checkpoints",
            "09_models/tokenizers",
            "logs",
            "temp",
            "outputs"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {directory}")
        
        return True
    
    def create_virtual_environment(self):
        """Create Python virtual environment"""
        print("\n🔧 Creating virtual environment...")
        
        venv_path = self.project_root / self.config['venv_name']
        
        if venv_path.exists():
            print(f"   ✅ Virtual environment already exists: {venv_path}")
            return True
        
        try:
            if self.system == "windows":
                subprocess.run([
                    sys.executable, "-m", "venv", str(venv_path)
                ], check=True, capture_output=True)
            else:
                subprocess.run([
                    sys.executable, "-m", "venv", str(venv_path)
                ], check=True, capture_output=True)
            
            print(f"   ✅ Virtual environment created: {venv_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("\n📦 Installing dependencies...")
        
        # Core dependencies
        dependencies = [
            "torch>=1.9.0",
            "transformers>=4.20.0",
            "tokenizers>=0.12.0",
            "datasets>=2.0.0",
            "accelerate>=0.20.0",
            "wandb>=0.12.0",
            "tqdm>=4.64.0",
            "numpy>=1.21.0",
            "pandas>=1.3.0",
            "requests>=2.28.0",
            "beautifulsoup4>=4.11.0",
            "lxml>=4.9.0",
            "scikit-learn>=1.1.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "jupyter>=1.0.0",
            "ipywidgets>=7.7.0"
        ]
        
        # System-specific dependencies
        if self.system == "windows":
            dependencies.extend([
                "pywin32>=304",
                "psutil>=5.9.0"
            ])
        else:
            dependencies.extend([
                "psutil>=5.9.0"
            ])
        
        # Install each dependency
        venv_python = self.project_root / self.config['venv_name'] / "bin" / "python"
        if self.system == "windows":
            venv_python = self.project_root / self.config['venv_name'] / "Scripts" / "python.exe"
        
        for dep in dependencies:
            try:
                print(f"   Installing {dep}...")
                subprocess.run([
                    str(venv_python), "-m", "pip", "install", dep
                ], check=True, capture_output=True)
                print(f"   ✅ {dep}")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to install {dep}: {e}")
                return False
        
        return True
    
    def create_requirements_file(self):
        """Create requirements.txt file"""
        print("\n📝 Creating requirements.txt...")
        
        requirements_content = """# London Historical LLM Requirements
# Core ML libraries
torch>=1.9.0
transformers>=4.20.0
tokenizers>=0.12.0
datasets>=2.0.0
accelerate>=0.20.0

# Data processing
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.1.0

# Web scraping and data collection
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0

# Visualization and monitoring
matplotlib>=3.5.0
seaborn>=0.11.0
wandb>=0.12.0

# Development tools
jupyter>=1.0.0
ipywidgets>=7.7.0
tqdm>=4.64.0

# System utilities
psutil>=5.9.0
"""
        
        if self.system == "windows":
            requirements_content += "\n# Windows specific\npywin32>=304\n"
        
        requirements_file = self.project_root / "requirements.txt"
        with open(requirements_file, 'w') as f:
            f.write(requirements_content)
        
        print(f"   ✅ Created: {requirements_file}")
        return True
    
    def create_environment_script(self):
        """Create environment activation script"""
        print("\n🔧 Creating environment activation script...")
        
        if self.system == "windows":
            script_content = f"""@echo off
REM London Historical LLM Environment Activation
echo 🏛️ Activating London Historical LLM Environment...

REM Activate virtual environment
call "{self.project_root}\\{self.config['venv_name']}\\Scripts\\activate.bat"

REM Set environment variables
set LONDON_LLM_ROOT={self.project_root}
set LONDON_LLM_DATA={self.config['data_dir']}
set LONDON_LLM_MODELS={self.config['models_dir']}

echo ✅ Environment activated!
echo 📁 Project root: %LONDON_LLM_ROOT%
echo 📊 Data directory: %LONDON_LLM_DATA%
echo 🤖 Models directory: %LONDON_LLM_MODELS%
echo.
echo Ready to start training your London Historical LLM! 🏛️✨
"""
            script_file = self.project_root / "activate_env.bat"
        else:
            script_content = f"""#!/bin/bash
# London Historical LLM Environment Activation
echo "🏛️ Activating London Historical LLM Environment..."

# Activate virtual environment
source "{self.project_root}/{self.config['venv_name']}/bin/activate"

# Set environment variables
export LONDON_LLM_ROOT="{self.project_root}"
export LONDON_LLM_DATA="{self.config['data_dir']}"
export LONDON_LLM_MODELS="{self.config['models_dir']}"

echo "✅ Environment activated!"
echo "📁 Project root: $LONDON_LLM_ROOT"
echo "📊 Data directory: $LONDON_LLM_DATA"
echo "🤖 Models directory: $LONDON_LLM_MODELS"
echo ""
echo "Ready to start training your London Historical LLM! 🏛️✨"
"""
            script_file = self.project_root / "activate_env.sh"
        
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        if self.system != "windows":
            os.chmod(script_file, 0o755)
        
        print(f"   ✅ Created: {script_file}")
        return True
    
    def save_config(self):
        """Save environment configuration"""
        print("\n💾 Saving environment configuration...")
        
        config_file = self.project_root / "environment_config.json"
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"   ✅ Configuration saved: {config_file}")
        return True
    
    def print_activation_instructions(self):
        """Print instructions for activating the environment"""
        print("\n" + "="*70)
        print("🎉 ENVIRONMENT SETUP COMPLETE!")
        print("="*70)
        print(f"📁 Project root: {self.project_root}")
        print(f"🐍 Python version: {self.config['python_version']}")
        print(f"💻 System: {self.config['system']}")
        print(f"📦 Virtual environment: {self.config['venv_name']}")
        
        print(f"\n🔧 To activate the environment:")
        if self.system == "windows":
            print(f"   {self.project_root}\\activate_env.bat")
            print(f"   OR")
            print(f"   {self.project_root}\\{self.config['venv_name']}\\Scripts\\activate")
        else:
            print(f"   source {self.project_root}/activate_env.sh")
            print(f"   OR")
            print(f"   source {self.project_root}/{self.config['venv_name']}/bin/activate")
        
        print(f"\n📚 Next steps:")
        print(f"   1. Activate the environment")
        print(f"   2. Run: cd 02_data_collection && python download_historical_data.py")
        print(f"   3. Run: cd 03_tokenizer && python train_tokenizer.py")
        print(f"   4. Run: cd 04_training && python train_model.py")
        
        print("="*70)

def main():
    """Main setup function"""
    print("🏛️ London Historical LLM - Environment Setup")
    print("=" * 50)
    
    setup = EnvironmentSetup()
    
    # Run setup steps
    steps = [
        ("Checking Python version", setup.check_python_version),
        ("Checking system requirements", setup.check_system_requirements),
        ("Creating directories", setup.create_directories),
        ("Creating virtual environment", setup.create_virtual_environment),
        ("Installing dependencies", setup.install_dependencies),
        ("Creating requirements.txt", setup.create_requirements_file),
        ("Creating activation script", setup.create_environment_script),
        ("Saving configuration", setup.save_config)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    # Print final instructions
    setup.print_activation_instructions()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
