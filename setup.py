#!/usr/bin/env python3
"""
Athena AI Setup Script
Helps configure Supabase and other services for development.
"""

import os
import sys
from pathlib import Path

def main():
    print("🏛️ Athena AI Setup Script")
    print("=" * 40)

    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Creating from .env.example...")
        if Path(".env.example").exists():
            env_file.write_text(Path(".env.example").read_text())
            print("✅ Created .env file")
        else:
            print("❌ .env.example not found")
            return

    # Read current .env
    env_content = env_file.read_text()
    print("\n📋 Current .env configuration:")

    supabase_url = ""
    supabase_key = ""
    openrouter_key = ""

    for line in env_content.split('\n'):
        if line.startswith('SUPABASE_URL='):
            supabase_url = line.split('=', 1)[1].strip()
        elif line.startswith('SUPABASE_KEY='):
            supabase_key = line.split('=', 1)[1].strip()
        elif line.startswith('OPENROUTER_API_KEY='):
            openrouter_key = line.split('=', 1)[1].strip()

    print(f"  SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Not set'}")
    print(f"  SUPABASE_KEY: {'✅ Set' if supabase_key else '❌ Not set'}")
    print(f"  OPENROUTER_API_KEY: {'✅ Set' if openrouter_key else '❌ Not set'}")

    if not supabase_url or not supabase_key:
        print("\n🚨 Supabase credentials required for authentication!")
        print("\n📝 Setup Instructions:")
        print("1. Go to https://supabase.com")
        print("2. Create a new project")
        print("3. Go to Settings > API")
        print("4. Copy 'Project URL' and 'anon public' key")
        print("5. Update your .env file with these values")

        # Ask user if they want to input values now
        if input("\n❓ Do you have Supabase credentials? (y/n): ").lower().startswith('y'):
            url = input("Enter SUPABASE_URL: ").strip()
            key = input("Enter SUPABASE_KEY: ").strip()

            if url and key:
                # Update .env file
                lines = env_content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('SUPABASE_URL='):
                        lines[i] = f'SUPABASE_URL={url}'
                    elif line.startswith('SUPABASE_KEY='):
                        lines[i] = f'SUPABASE_KEY={key}'

                env_file.write_text('\n'.join(lines))
                print("✅ Updated .env file")
            else:
                print("❌ Invalid input")

    if not openrouter_key:
        print("\n🤖 OpenRouter API key required for AI features!")
        print("1. Go to https://openrouter.ai/keys")
        print("2. Create an API key")
        print("3. Update OPENROUTER_API_KEY in your .env file")

    print("\n🎯 Next steps:")
    print("1. Configure your .env file with API keys")
    print("2. Run: streamlit run streamlit_app.py")
    print("3. Or use Development Mode if you just want to test the UI")

if __name__ == "__main__":
    main()