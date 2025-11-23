from qiskit_ibm_runtime import QiskitRuntimeService

# Create a my_credentials.py as a duplicate of this file
QiskitRuntimeService.save_account(
token="<your-api-key>", # Use the 44-character API_KEY you created and saved from the IBM Quantum Platform Home dashboard
instance="<CRN>", # Optional
)

# To use in a .py
from qiskit_ibm_runtime import QiskitRuntimeService

# Run every time you need the service
service = QiskitRuntimeService()