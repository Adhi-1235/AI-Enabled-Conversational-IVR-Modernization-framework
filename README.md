# Python Middleware Example

This folder contains a Python implementation of the same middleware logic
used in the Node/Express example. It demonstrates that you can build the
integration layer in Python if desired.

## Getting started

1. Create a virtual environment and install dependencies:

   ```bash
   cd middleware_py
   python -m venv venv
   venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```

2. Run the server:

   ```bash
   uvicorn app:app --reload --port 3000
   ```

3. The endpoints (`/session`, `/session/{id}/input`, etc.) behave exactly like
the Node version, so the web simulator and test script will work unchanged.

## Notes

- The menu definitions and session state storage are identical to the
  Node implementation.
- You can extend this service with real data lookups or provider connectors
  in Python as needed.