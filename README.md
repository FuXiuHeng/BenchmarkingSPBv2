# BenchmarkingSPBv2
Author: Fu Xiu Heng

This code is written for the purpose of thesis in UNSW 2019 on the topic of Benchmarking Secure Private Blockchain-based (SPB)
solution to energy trading. The primary purpose of this code is to run simulations of the SPB solution and a baseline solution,
and log performance results of these solutions. The steps to doing so are outlined below.

## Running a Simulation
To run a simulation, there are several steps involved:
### 1. Installing dependencies
    - Note: hese are written with Linux OS in mind
    - To install the dependencies, run the two scripts 
      - `./scripts/install_apt_dependencies.sh` 
      - `./scripts/isntall_pip3_dependencies.sh`

### 2. Configuring the settings 
    - There are two settings file `settings/settings.py` and `settings/settings.sh`
    - Change the number of nodes, port numbers etc
    - **Note**: ensure both setting files have values that match up because I wrote some scripts in Bash and some in Python,
    and didn't end up unifying them.

### 3. Configuring MySQL
    - This step is **only needed for the SPB** simulation as it stores CTP transactions in MySQL database.
    - 
    - ```
      mysql -u root -p
      GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost' IDENTIFIED BY 'password';
      ```
    
    
    mysql -u root -p
GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost' IDENTIFIED BY 'password';
\q

3. Run the ethereum nodes

Scripts in this code base are written in either Bash or Python.



