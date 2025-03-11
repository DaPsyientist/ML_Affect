import subprocess
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Now you can import other scripts
import process_ema
import process_eda_and_combine

# Function to install packages from a requirements file
def install_packages(requirements_file):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install','--user', '-r', requirements_file])

# Path to your requirements file
requirements_file = 'requirements.txt'
install_packages(requirements_file)

if __name__ == "__main__":
    # List the files specified in the command line
    inputFiles = sys.argv[1:] 
    User_ID = inputFiles[0]
    EMA_DF = inputFiles[1]
    
# Check if EMA_Processed.csv exists
ema_processed_file = './EMA_Processed.csv'
if not os.path.exists(ema_processed_file):
    # Run EMA processing script if EMA_Processed.csv doesn't exist
    process_ema.run(EMA_DF)

# Run EDA processing and combine script
process_eda_and_combine.run(User_ID)
