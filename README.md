# Running Applications in a Standalone Environment

This document outlines the steps to run the application in a standalone browser environment, along with instructions for developers setting up their local development environment.

## 🏃 Running the Application 

### ⬇️ Step 1: Download/Copy the application to a local directory

Download the application files to your desired local directory. For example, you might choose `C:\test\app` on Windows or `/home/user/app` on Linux/macOS.

### 💻 Step 2: Start the local host server

This application uses a simple local host for serving the files. Follow the instructions below for your operating system:

**Windows:**

1. Open the folder `run/win`
2. Right click `start.ps1` and click `Run with PowerShell`

**Linux/macOS:**

1. Open a `terminal`.
2. Navigate to the directory `run/linux`, and run `./start.sh`

## ⚙️ For Developers

### Setting up the development environment

This project uses `conda` for environment management.  Follow these steps to set up your local development environment:

1. **Install conda (if you haven't already):**  Download and install conda from [https://conda.io/](https://conda.io/).

2. **Create the environment:** Open a terminal or command prompt and navigate to the project directory (where the `env.yml` file is located). Then, run the following command:
   ```
   conda env create -f env.yml
   ```

3. **Obtain Pyscript core (Optional):** Install Pyscript using `npm`
   ```
   npm i @pyscript/core
   ```
   The above should give you many `js` files located in `node_modules/@pyscript/core/dist`, you need to copy the entire `dist` folder to your working directory

4. **Obtain PyOdide (Optional):**: `PyOdide` is needed if (1) you want to run applications offline, and (2) 3rd party libraries are needed:
   - Download the latest from `https://github.com/pyodide/pyodide/releases`
   - For package comes with script to select dependancies, we can run the script to copy the required dependencies to the working directory. For example:
      * for `casual_learn_without_internet`, we can run `python copy_pyodide.py`. 
      * Otherwise, copy the entire downloaded packages to `<Application>/etc/pyodide`. For example: `cp -rf cp -rf pyodide/pyodide* <Application>/etc/pyodide`

5. **Create PyOdide package (Optional):**
   - Start a PyOdide docker container: from the PyOdide repository, we can run:
      ```
      ./run_docker --root
      ```
   
    - Update/install necessary librairies such as:
      ```
      apt-get update
      apt-get install vim -y
      ```

   - Install emsdk (optional):
      ```
      cd /tmp
      sudo apt-get install git -y
      git clone https://github.com/emscripten-core/emsdk.git
      cd emsdk
      ./emsdk install 3.1.58
      ./emsdk activate 3.1.58
      source ./emsdk_env.sh
      ```

   - Install the packages that we need inside the container:
      - `cd /tmp`
      - `pyodide skeleton pypi <Package name>`. For example, `pyodide skeleton pypi causal-learn`
      - `pyodide build-recipes <Package name> --install`. For example, `pyodide build-recipes causal-learn --install`

   - Copy the wheel file out. For example if the wheel file located in `/tmp/pkgs/dist/<PKG>.whl`.
      - Get the container ID: `docker ps -a`, e.g., if the ID is `XXXX`
      - Copy the wheel file to local:  `docker cp XXXX:/tmp/pkgs/dist/<PKG>.whl /tmp/<PKG>.whl`. For example, `docker cp 45279f929dd1:/tmp/pkgs/dist/causal_learn-0.1.4.0-py3-none-any.whl /tmp`
      - Copy the `pyodide-lock.json` to local, e.g., `docker cp 45279f929dd1:/tmp/pkgs/dist/pyodide-lock.json /tmp`, and add the application to the application's original `pyodide-lock.json` (e.g., `etc/pyodide/pyodide-lock.json`)



https://pyodide.org/en/stable/development/building-and-testing-packages.html#building-and-testing-packages-out-of-tree