#!/bin/bash

curl -o complaints.csv.zip https://files.consumerfinance.gov/ccdb/complaints.csv.zip

# Check the operating system
OS="$(uname)"

#!/bin/bash

# Function to install unzip for macOS if not present
install_unzip_macos() {
    if ! command -v unzip &> /dev/null; then
        echo "unzip is not installed. Installing..."
        # Install unzip using Homebrew (assuming Homebrew is installed)
        brew install unzip
    else
        echo "unzip is already installed."
    fi
}

if [ "$OS" == "Darwin" ]; then
    # macOS commands
    echo "macOS detected."

    # Get macOS version
    macOS_version=$(sw_vers -productVersion)
    echo "macOS version: $macOS_version"

    # Check for specific macOS versions (Ventura, Sonoma, etc.)
    case $macOS_version in
        13*) echo "macOS Ventura detected.";;
        12*) echo "macOS Sonoma detected.";; # Assuming macOS 12 is Sonoma
        *) echo "Other macOS version detected.";;
    esac

    # Install unzip if not present
    install_unzip_macos
elif [ "$OS" == "Linux" ]; then
    # Linux commands
    echo "Linux detected."
    if ! command -v unzip &> /dev/null; then
        echo "unzip is not installed. Installing..."
        # Install unzip for Linux
        sudo apt-get update
        sudo apt-get install unzip
    else
        echo "unzip is already installed."
    fi
else
    echo "Unsupported operating system."
fi

# unzip the file
unzip complaints.csv.zip


