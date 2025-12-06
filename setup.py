# setup.py
import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print("Instalando dependencias...")
packages = ["streamlit", "pymysql", "pandas", "plotly"]

for package in packages:
    try:
        install_package(package)
        print(f"✅ {package} instalado")
    except:
        print(f"⚠️  Error instalando {package}")

print("\n✅ Instalación completada!")