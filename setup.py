"""
Setup script for Hand Hockey Discord Bot
Helps with initial installation and configuration
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except FileNotFoundError:
        print("❌ requirements.txt not found!")
        return False

def setup_environment():
    """Setup environment configuration"""
    print("🔧 Setting up environment configuration...")
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print("⚠️  .env file already exists. Skipping...")
        return True
    
    if not env_example_path.exists():
        print("❌ .env.example not found!")
        return False
    
    try:
        shutil.copy(env_example_path, env_path)
        print("✅ Created .env file from template")
        
        print("\n🔑 IMPORTANT: Edit .env file with your Discord bot token!")
        print("   1. Go to https://discord.com/developers/applications")
        print("   2. Create a new bot application")
        print("   3. Copy the bot token")
        print("   4. Paste it in the .env file")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_cogs_directory():
    """Create cogs directory if it doesn't exist"""
    cogs_dir = Path("cogs")
    if not cogs_dir.exists():
        cogs_dir.mkdir()
        print("✅ Created cogs directory")
    
    # Create __init__.py for the cogs package
    init_file = cogs_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        print("✅ Created cogs/__init__.py")

def validate_project_structure():
    """Validate that all required files exist"""
    print("🔍 Validating project structure...")
    
    required_files = [
        "main.py",
        "config.py", 
        "utils.py",
        "game_logic.py",
        "requirements.txt",
        ".env.example",
        "cogs/match_management.py",
        "cogs/team_setup.py",
        "cogs/game_flow.py",
        "cogs/commentary.py",
        "cogs/player_stats.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files are present")
    return True

def main():
    """Main setup function"""
    print("🏒 Hand Hockey Discord Bot Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Validate project structure
    if not validate_project_structure():
        print("\n❌ Setup failed due to missing files")
        return False
    
    # Create necessary directories
    create_cogs_directory()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        return False
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Setup failed during environment configuration")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Edit .env file with your Discord bot token")
    print("   2. Run: python main.py")
    print("   3. Invite the bot to your Discord server")
    print("\n🔗 Bot invite link (replace CLIENT_ID):")
    print("   https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=2048&scope=bot")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)
